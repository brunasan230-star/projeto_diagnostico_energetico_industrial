# Auditoria do CSV do ITAC (para a seção de dados do artigo)

Arquivo: `ITAC_MECS_2022_completecase_17_setores.csv` (8.832 linhas × 64 colunas). O script que gerou o arquivo a partir do ITAC bruto não está disponível; os filtros abaixo foram conferidos no próprio arquivo.

## Filtros conferidos

| Filtro declarado | Conferência no CSV |
|---|---|
| Uma linha por avaliação | 8.832 `assessment_id` distintos, sem duplicatas |
| Período FY 2005–2025 | `assessment_fy` de 2005 a 2025; de 239 a 582 avaliações por ano |
| Manufatura | todos os `naics` têm 6 dígitos e começam com 31, 32 ou 33 |
| 17 subsetores NAICS3 com perfil MECS completo | 17 valores de `naics3`; as cinco participações elétricas sem ausentes |
| Participação = uso final / total do subsetor | `share_*` = coluna do uso final ÷ `Total fuel consumption`, diferença máxima 1e-16 |
| Placebo | `placebo_share_*` = mesma participação de outro subsetor (permutação fixa entre os 17) |

Cobertura: 50 centros de avaliação (IACs) e 51 estados.

## O que o CSV tem além do que o experimento usa

- Rótulos de outras famílias, não usados na Q1: `vapor` (14,2%), `recuperacao_calor` (30,5%), `label_rescheduling` (6,8%), `label_demand_controller` (1,6%) e `label_thermal_storage` (0,4%).
- Erro-padrão relativo do MECS (`rse_*`), até 35,8% nas participações usadas. Serve como ressalva sobre a precisão do perfil setorial.
- Colunas brutas da tabela de uso final do MECS por subsetor.

## Pontos de atenção

- **Atributos em log1p:** os seis atributos numéricos da avaliação já estão transformados. `demand_cost_usd_year` está em US$ e recebe log1p no pipeline.
- **Custo de demanda:** falta em 1.197 avaliações (13,6%). Há 24 valores ≤ US$ 1, dos quais 2 são praticamente zero (1e-10), o que sugere zero registrado como ausência. Ficaram como estão; a transformação log1p reduz o efeito deles.
- **Rótulos:** derivados das recomendações do ITAC (códigos ARC 2.41 motores, 2.72 HVAC, 2.26 resfriamento). Rótulo 0 significa recomendação não registrada, não equipamento inexistente.

## Como descrever no artigo

"A base integrada foi construída na Etapa 1 a partir do ITAC e do MECS 2022: avaliações de manufatura (NAICS 31–33) entre os anos fiscais 2005 e 2025, unidas ao perfil de uso final de eletricidade do subsetor NAICS3 e restritas aos 17 subsetores com as cinco participações publicadas. O resultado tem 8.832 avaliações de 50 centros. Os filtros e a junção foram conferidos no arquivo final (Tabela X)."
