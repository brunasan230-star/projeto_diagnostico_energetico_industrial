"""Rotas do Experimento II: transformação direta (modelo temporal) e semântica (RDF + SHACL)."""
import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd
from pyshacl import validate
from rdflib import RDF, RDFS, XSD, BNode, Graph, Literal, Namespace, URIRef

KIT = Namespace("https://example.org/ind2622/kit#")
S4ENER = Namespace("https://saref.etsi.org/saref4ener/")
SH = Namespace("http://www.w3.org/ns/shacl#")

CAMPOS_TAREFA = ["duration", "usages", "release", "deadline"]


# ---------------------------------------------------------------- rota direta
def rota_direta_tabelas(inst):
    """JSON -> duas tabelas (blocos e precedências), como entrada típica de um modelo de programação."""
    jobs = pd.DataFrame([{
        "id": j.get("id"), "release": j.get("release"), "deadline": j.get("deadline"),
        "duration": j.get("duration"), "potencia": (j.get("usages") or {}).get("0"),
        "superjob": (j.get("additional") or {}).get("superjob_id"),
    } for j in inst["jobs"]])
    prec = pd.DataFrame([{"de": j.get("id"), "para": int(s), "lag": v.get("lag")}
                         for j in inst["jobs"] for s, v in (j.get("successors") or {}).items()],
                        columns=["de", "para", "lag"])
    return jobs, prec


def grafo_temporal(jobs, prec):
    """Arestas do problema temporal simples: s_v - s_u <= w. Nó 0 é a origem do tempo."""
    pos = {jid: k + 1 for k, jid in enumerate(jobs["id"])}
    u, v, w = [], [], []
    for jid, r, d, p in jobs[["id", "release", "deadline", "duration"]].itertuples(index=False):
        k = pos[jid]
        u += [k, 0]; v += [0, k]; w += [-r, d - p]          # s_k >= r ;  s_k <= d - p
    for a, b, lag in prec.itertuples(index=False):
        u.append(pos[b]); v.append(pos[a]); w.append(-lag)   # s_b >= s_a + lag
    return np.array(u), np.array(v), np.array(w, dtype=float), len(jobs) + 1


def viavel(u, v, w, n):
    """Bellman-Ford vetorizado: há programação viável se não existe ciclo negativo."""
    ok = ~np.isnan(w)
    u, v, w = u[ok], v[ok], w[ok]
    dist = np.zeros(n)
    for _ in range(n):
        novo = dist.copy()
        np.minimum.at(novo, v, dist[u] + w)
        if np.array_equal(novo, dist):
            return True
        dist = novo
    return False


def rota_direta(inst):
    """Devolve (situação, detalhe). Situação: 'aceita', 'inviavel' ou 'falha'."""
    try:
        jobs, prec = rota_direta_tabelas(inst)
        u, v, w, n = grafo_temporal(jobs, prec)
        return ("aceita", None) if viavel(u, v, w, n) else ("inviavel", "modelo temporal sem solução")
    except Exception as e:  # erro de execução ao montar o modelo
        return "falha", f"{type(e).__name__}: {e}"


def solucao_viavel_direta(inst, inicio):
    jobs, prec = rota_direta_tabelas(inst)
    u, v, w, n = grafo_temporal(jobs, prec)
    s = np.concatenate([[0.0], jobs["id"].map(inicio).to_numpy(float)])
    return bool(np.all(s[v] - s[u] <= w + 1e-9))


def direta_para_json(jobs, prec):
    out = []
    for r in jobs.itertuples(index=False):
        succ = {str(int(b)): {"lag": int(l)} for a, b, l in prec[prec.de == r.id].itertuples(index=False)}
        out.append({"id": int(r.id), "release": int(r.release), "deadline": int(r.deadline),
                    "duration": int(r.duration), "usages": {"0": float(r.potencia)},
                    "superjob_id": int(r.superjob), "successors": succ})
    return out


# ------------------------------------------------------------- rota semântica
def lit(v):
    return Literal(v)


def para_rdf(inst, inicio=None):
    """JSON -> grafo RDF. Bloco = s4ener:Slot; tarefa contínua = s4ener:PowerSequence; precedência em extensão local."""
    g = Graph()
    g.bind("kit", KIT); g.bind("s4ener", S4ENER)
    no_inst = KIT[f"inst_{inst['id']}"]
    g.add((no_inst, RDF.type, KIT.Instancia))
    seqs = {}
    for j in inst["jobs"]:
        b = KIT[f"inst_{inst['id']}_bloco_{j.get('id')}"]
        g.add((b, RDF.type, KIT.Bloco))
        g.add((no_inst, KIT.temBloco, b))
        for campo, prop in [("id", KIT.id), ("duration", KIT.duracao), ("release", KIT.inicioMaisCedo),
                            ("deadline", KIT.fimMaisTarde)]:
            if campo in j:
                g.add((b, prop, lit(j[campo])))
        for rec, val in (j.get("usages") or {}).items():
            g.add((b, KIT.potencia, lit(val)))
        sj = (j.get("additional") or {}).get("superjob_id")
        if sj is not None:
            s = seqs.setdefault(sj, KIT[f"inst_{inst['id']}_seq_{sj}"])
            g.add((s, RDF.type, KIT.SequenciaContinua))
            g.add((s, KIT.superjob, lit(sj)))
            g.add((no_inst, KIT.temSequencia, s))
            g.add((b, KIT.pertenceA, s))
        if inicio is not None and j.get("id") in inicio:
            g.add((b, KIT.inicioProgramado, lit(inicio[j["id"]])))
        for alvo, attr in (j.get("successors") or {}).items():
            p = KIT[f"inst_{inst['id']}_bloco_{j.get('id')}_prec_{alvo}"]
            g.add((p, RDF.type, KIT.Precedencia))
            g.add((p, KIT.de, b))
            g.add((p, KIT.para, KIT[f"inst_{inst['id']}_bloco_{alvo}"]))
            if "lag" in attr:
                g.add((p, KIT.defasagem, lit(attr["lag"])))
            g.add((no_inst, KIT.temPrecedencia, p))
    return g


def rdf_para_json(g):
    q = """SELECT ?id ?r ?d ?p ?w ?sj WHERE { ?b a kit:Bloco ; kit:id ?id ; kit:inicioMaisCedo ?r ;
           kit:fimMaisTarde ?d ; kit:duracao ?p ; kit:potencia ?w ; kit:pertenceA/kit:superjob ?sj }"""
    jobs = {int(r.id): {"id": int(r.id), "release": int(r.r), "deadline": int(r.d), "duration": int(r.p),
                        "usages": {"0": float(r.w)}, "superjob_id": int(r.sj), "successors": {}}
            for r in g.query(q, initNs={"kit": KIT})}
    q2 = """SELECT ?a ?b ?l WHERE { ?x a kit:Precedencia ; kit:de/kit:id ?a ; kit:para/kit:id ?b ; kit:defasagem ?l }"""
    for r in g.query(q2, initNs={"kit": KIT}):
        jobs[int(r.a)]["successors"][str(int(r.b))] = {"lag": int(r.l)}
    return [jobs[k] for k in sorted(jobs)]


ONTOLOGIA = """
@prefix kit: <https://example.org/ind2622/kit#> .
@prefix s4ener: <https://saref.etsi.org/saref4ener/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
kit:Bloco rdfs:subClassOf s4ener:Slot ;
    rdfs:comment "Bloco de uma tarefa decomposta: duração e potência constantes." .
kit:SequenciaContinua rdfs:subClassOf s4ener:PowerSequence ;
    rdfs:comment "Tarefa-base (superjob) cujos blocos são executados em sequência, sem intervalo." .
kit:Precedencia rdfs:comment "Extensão local: o bloco 'para' só começa 'defasagem' passos após o início do bloco 'de'. Defasagem negativa fecha o ciclo que impõe contiguidade." .
"""

SHAPES = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix kit: <https://example.org/ind2622/kit#> .

kit:BlocoShape a sh:NodeShape ; sh:targetClass kit:Bloco ;
  sh:property [ sh:path kit:id ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:integer ;
                sh:message "R0 identificador ausente ou inválido" ] ;
  sh:property [ sh:path kit:duracao ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:integer ;
                sh:minExclusive 0 ; sh:message "R1 duração ausente, não inteira ou não positiva" ] ;
  sh:property [ sh:path kit:potencia ; sh:minCount 1 ; sh:maxCount 1 ;
                sh:or ( [ sh:datatype xsd:double ] [ sh:datatype xsd:integer ] [ sh:datatype xsd:decimal ] ) ;
                sh:minInclusive 0 ; sh:message "R2 potência ausente, não numérica ou negativa" ] ;
  sh:property [ sh:path kit:inicioMaisCedo ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:integer ;
                sh:minInclusive 0 ; sh:message "R3 início da janela ausente ou inválido" ] ;
  sh:property [ sh:path kit:fimMaisTarde ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:integer ;
                sh:message "R3 fim da janela ausente ou inválido" ] ;
  sh:property [ sh:path kit:pertenceA ; sh:minCount 1 ; sh:maxCount 1 ; sh:class kit:SequenciaContinua ;
                sh:message "R6 bloco sem sequência de origem" ] .

kit:PrecedenciaShape a sh:NodeShape ; sh:targetClass kit:Precedencia ;
  sh:property [ sh:path kit:para ; sh:minCount 1 ; sh:maxCount 1 ; sh:class kit:Bloco ;
                sh:message "R5 precedência aponta para bloco inexistente" ] ;
  sh:property [ sh:path kit:defasagem ; sh:minCount 1 ; sh:maxCount 1 ; sh:datatype xsd:integer ;
                sh:message "R5 defasagem ausente ou não inteira" ] .

kit:InstanciaShape a sh:NodeShape ; sh:targetClass kit:Instancia ;
  sh:sparql [ sh:message "R4 janela do bloco menor que a duração" ;
    sh:select '''PREFIX kit: <https://example.org/ind2622/kit#>
      SELECT $this ?value WHERE { $this kit:temBloco ?value .
        ?value kit:inicioMaisCedo ?r ; kit:fimMaisTarde ?d ; kit:duracao ?p .
        FILTER (isNumeric(?r) && isNumeric(?d) && isNumeric(?p) && ?r + ?p > ?d) }''' ] ;
  sh:sparql [ sh:message "R7 janela da sequência não comporta a soma das durações dos blocos" ;
    sh:select '''PREFIX kit: <https://example.org/ind2622/kit#>
      SELECT $this ?value WHERE {
        { SELECT $this ?value (MIN(?r) AS ?ini) (MAX(?d) AS ?fim) (SUM(?p) AS ?tot) WHERE {
            $this kit:temBloco ?b . ?b kit:pertenceA ?value ;
              kit:inicioMaisCedo ?r ; kit:fimMaisTarde ?d ; kit:duracao ?p .
            FILTER (isNumeric(?r) && isNumeric(?d) && isNumeric(?p)) } GROUP BY $this ?value }
        FILTER (?ini + ?tot > ?fim) }''' ] ;
  sh:sparql [ sh:message "R8 sequência não contígua: defasagens do ciclo de blocos não somam zero" ;
    sh:select '''PREFIX kit: <https://example.org/ind2622/kit#>
      SELECT $this ?value WHERE {
        { SELECT $this ?value (SUM(?l) AS ?soma) (COUNT(?x) AS ?n) WHERE {
            $this kit:temPrecedencia ?x . ?x kit:de/kit:pertenceA ?value ; kit:defasagem ?l .
            FILTER (isNumeric(?l)) } GROUP BY $this ?value }
        FILTER (?n > 1 && ?soma != 0) }''' ] ;
  sh:sparql [ sh:message "R9 precedência incompatível com as janelas" ;
    sh:select '''PREFIX kit: <https://example.org/ind2622/kit#>
      SELECT $this ?value WHERE { $this kit:temPrecedencia ?x .
        ?x kit:de ?a ; kit:para ?value ; kit:defasagem ?l .
        ?a kit:inicioMaisCedo ?ra . ?value kit:fimMaisTarde ?db ; kit:duracao ?pb .
        FILTER (isNumeric(?ra) && isNumeric(?db) && isNumeric(?pb) && isNumeric(?l) && ?ra + ?l > ?db - ?pb) }''' ] .
"""

SHAPES_SOLUCAO = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix kit: <https://example.org/ind2622/kit#> .
kit:SolucaoShape a sh:NodeShape ; sh:targetClass kit:Instancia ;
  sh:sparql [ sh:message "S1 bloco programado fora da janela" ;
    sh:select '''PREFIX kit: <https://example.org/ind2622/kit#>
      SELECT $this ?value WHERE { $this kit:temBloco ?value .
        ?value kit:inicioProgramado ?s ; kit:inicioMaisCedo ?r ; kit:fimMaisTarde ?d ; kit:duracao ?p .
        FILTER (?s < ?r || ?s + ?p > ?d) }''' ] ;
  sh:sparql [ sh:message "S2 precedência violada na programação" ;
    sh:select '''PREFIX kit: <https://example.org/ind2622/kit#>
      SELECT $this ?value WHERE { $this kit:temPrecedencia ?x .
        ?x kit:de ?a ; kit:para ?value ; kit:defasagem ?l .
        ?a kit:inicioProgramado ?sa . ?value kit:inicioProgramado ?sb .
        FILTER (?sb < ?sa + ?l) }''' ] .
"""

_shapes = Graph().parse(data=SHAPES, format="turtle")
_shapes_sol = Graph().parse(data=SHAPES_SOLUCAO, format="turtle")


def violacoes(g, shapes=None):
    conforma, rel, txt = validate(g, shacl_graph=shapes or _shapes, advanced=True, inference="none")
    if not isinstance(rel, Graph):
        raise RuntimeError(txt)
    if conforma:
        return []
    out = []
    for r in rel.subjects(RDF.type, SH.ValidationResult):
        msg = str(rel.value(r, SH.resultMessage))
        foco = rel.value(r, SH.focusNode)
        if "_bloco_" not in str(foco) and "_seq_" not in str(foco):  # restrição da instância: o valor aponta o elemento
            foco = rel.value(r, SH.value)
        out.append((msg.split(" ")[0], str(foco)))
    return out


def rota_semantica(inst):
    try:
        v = violacoes(para_rdf(inst))
    except Exception as e:
        return "falha", f"{type(e).__name__}: {e}", []
    return ("rejeitada" if v else "aceita"), (sorted({r for r, _ in v}) or None), v


# ------------------------------------------------------------ injeção de erros
def _blocos_de_sequencias_longas(inst, rng):
    from collections import defaultdict
    g = defaultdict(list)
    for j in inst["jobs"]:
        g[j["additional"]["superjob_id"]].append(j)
    longas = [v for v in g.values() if len(v) > 1]
    return longas[rng.integers(len(longas))] if longas else None


def injetar(inst, tipo, rng):
    """Devolve (instância alterada, id do bloco alterado) ou (None, None) se o tipo não se aplica."""
    x = copy.deepcopy(inst)
    J = x["jobs"]
    j = J[rng.integers(len(J))]
    if tipo == "E1_janela_menor_que_duracao":
        j["deadline"] = j["release"] + j["duration"] - 1
    elif tipo == "E2_duracao_zero":
        j["duration"] = 0
    elif tipo == "E3_potencia_negativa":
        j["usages"]["0"] = -abs(j["usages"]["0"]) - 1
    elif tipo == "E4_precedencia_inexistente":
        j["successors"][str(len(J) + 7)] = {"lag": 0, "drain_factor": 0.0, "max_recharge": 0}
    elif tipo == "E5_campo_ausente":
        del j["deadline"]
    elif tipo == "E6_tipo_invalido":
        j["duration"] = str(j["duration"])
    elif tipo in ("E7_janela_da_sequencia", "E8_contiguidade_quebrada", "E9_ciclo_inviavel"):
        seq = _blocos_de_sequencias_longas(x, rng)
        if seq is None:
            return None, None
        ids = {b["id"] for b in seq}
        if tipo == "E7_janela_da_sequencia":
            ini = min(b["release"] for b in seq)
            tot = sum(b["duration"] for b in seq)
            folga_min = max(b["duration"] for b in seq)
            novo_fim = ini + tot - 1
            if novo_fim < ini + folga_min:
                return None, None
            for b in seq:
                b["release"], b["deadline"] = ini, novo_fim
            j = seq[0]
        else:
            ret = next(b for b in seq for s, v in b["successors"].items() if int(s) in ids and v["lag"] < 0)
            alvo = next(s for s, v in ret["successors"].items() if v["lag"] < 0)
            ret["successors"][alvo]["lag"] += (-5 if tipo == "E8_contiguidade_quebrada" else 5)
            j = ret
    else:
        raise ValueError(tipo)
    return x, j["id"]


TIPOS = ["E1_janela_menor_que_duracao", "E2_duracao_zero", "E3_potencia_negativa", "E4_precedencia_inexistente",
         "E5_campo_ausente", "E6_tipo_invalido", "E7_janela_da_sequencia", "E8_contiguidade_quebrada",
         "E9_ciclo_inviavel"]
