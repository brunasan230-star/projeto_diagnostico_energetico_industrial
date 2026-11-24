"""Controle da Q2: as mesmas regras R0-R9 da rota semântica, escritas direto em Python sobre o JSON.

Cada violação vira (regra, elemento), com o elemento no mesmo formato da rota semântica
(..._bloco_<id>, ..._bloco_<id>_prec_<alvo>, ..._seq_<superjob>), para medir a localização do mesmo jeito.
"""
from collections import defaultdict


def _inteiro(v):
    return isinstance(v, int) and not isinstance(v, bool)


def _numero(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def violacoes_python(inst):
    pre = f"inst_{inst['id']}"
    out = []
    jobs = inst["jobs"]
    ids = {j.get("id") for j in jobs}
    por_id = {j.get("id"): j for j in jobs}
    seqs = defaultdict(list)

    for j in jobs:
        b = f"{pre}_bloco_{j.get('id')}"
        if not _inteiro(j.get("id")):
            out.append(("R0", b))
        d = j.get("duration")
        if not (_inteiro(d) and d > 0):
            out.append(("R1", b))
        pot = list((j.get("usages") or {}).values())
        if len(pot) != 1 or not _numero(pot[0]) or pot[0] < 0:
            out.append(("R2", b))
        r, f = j.get("release"), j.get("deadline")
        if not (_inteiro(r) and r >= 0):
            out.append(("R3", b))
        if not _inteiro(f):
            out.append(("R3", b))
        sj = (j.get("additional") or {}).get("superjob_id")
        if sj is None:
            out.append(("R6", b))
        else:
            seqs[sj].append(j)
        if _numero(r) and _numero(f) and _numero(d) and r + d > f:
            out.append(("R4", b))
        for alvo, attr in (j.get("successors") or {}).items():
            p = f"{b}_prec_{alvo}"
            if int(alvo) not in ids:
                out.append(("R5", p))
            if not _inteiro(attr.get("lag")):
                out.append(("R5", p))

    for sj, blocos in seqs.items():
        s = f"{pre}_seq_{sj}"
        ok = [x for x in blocos if all(_numero(x.get(k)) for k in ("release", "deadline", "duration"))]
        if ok and min(x["release"] for x in ok) + sum(x["duration"] for x in ok) > max(x["deadline"] for x in ok):
            out.append(("R7", s))
        lags = [a["lag"] for x in blocos for a in (x.get("successors") or {}).values() if _numero(a.get("lag"))]
        if len(lags) > 1 and sum(lags) != 0:
            out.append(("R8", s))

    for j in jobs:
        for alvo, attr in (j.get("successors") or {}).items():
            k = por_id.get(int(alvo))
            lag, ra = attr.get("lag"), j.get("release")
            if k is None or not all(_numero(v) for v in (lag, ra, k.get("deadline"), k.get("duration"))):
                continue
            if ra + lag > k["deadline"] - k["duration"]:
                out.append(("R9", f"{pre}_bloco_{alvo}"))
    return out


def rota_direta_validada(inst):
    """Mesma rota direta, mas com as regras checadas antes do modelo temporal."""
    try:
        v = violacoes_python(inst)
    except Exception as e:
        return "falha", f"{type(e).__name__}: {e}", []
    return ("rejeitada" if v else "aceita"), (sorted({r for r, _ in v}) or None), v
