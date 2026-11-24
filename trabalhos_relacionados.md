# Trabalhos relacionados: levantamento e análise crítica

Os trabalhos se dividem em quatro frentes. Nenhum deles cobre ao mesmo tempo o uso de conhecimento setorial estruturado para priorizar recomendações de auditoria e a preservação de restrições operacionais na preparação de dados de flexibilidade. É nessa interseção que o projeto se posiciona.

## 1. Dados de auditorias energéticas industriais (IAC/ITAC)

| Trabalho | O que fez | Limitação em relação ao nosso problema | Como o projeto se diferencia |
|---|---|---|---|
| Anderson e Newell (2004) | Modelou com logit de efeitos fixos a decisão de adotar os projetos recomendados pelas auditorias IAC. Concluiu que cerca de metade é rejeitada, sobretudo por razões econômicas | Explica a **adoção** das recomendações, não **quais** recomendações fazer; é um modelo explicativo, sem validação fora da amostra | Prevê quais famílias recomendar para uma planta ainda não auditada, com validação em setores não vistos |
| Blass et al. (2014) | Analisou 5.779 recomendações a 752 PMEs e mostrou que o envolvimento de gestores de operações aumenta a implementação | Foco organizacional; não usa perfil energético do setor nem tarefa preditiva | Usa o perfil setorial do MECS como variável e testa se ele melhora a previsão |
| Sarswatula, Pugh e Prabhu (2022) | Aplicou regressão e classificação (incluindo Random Forest e XGBoost) aos dados do IAC para modelar consumo de energia; Random Forest foi o melhor | Prevê **consumo**, não recomendações; validação aleatória, sem separar setores ou períodos; o alvo de classificação não é claramente definido | Prevê **recomendações**, com validação temporal e por setor e com controles (placebo, aleatório, estatístico) que isolam o efeito da informação externa |
| Miera et al. (2025) | Revisou 20.290 avaliações e 151.198 recomendações do IAC (1981–2022): taxa de implementação de 47% e análise por subsetor e tipo de energia | Estudo descritivo, sem modelo preditivo | Transforma as diferenças entre subsetores, que eles descrevem, em variáveis de um modelo, e mede o ganho |

**Leitura crítica.** A literatura com o IAC é sobretudo econométrica ou descritiva. Os poucos trabalhos de aprendizado de máquina validam com partições aleatórias, o que deixa o mesmo setor no treino e no teste e superestima o desempenho para plantas de setores novos. O nosso projeto ataca justamente esse ponto.

## 2. Flexibilidade industrial e o benchmark do KIT

| Trabalho | O que fez | Limitação | Diferencial do projeto |
|---|---|---|---|
| Ludwig et al. (2019) | Criou o benchmark de 1.764 instâncias a partir de dados reais de seis máquinas de uma fábrica de eletrônicos, decompondo tarefas em blocos ligados por precedências com defasagem | Foco em avaliar algoritmos de escalonamento. As próprias autoras apontam que a decomposição em blocos é uma aproximação e que há instâncias sem solução nos maiores níveis de decomposição, mas a regra de contiguidade fica implícita no formato e as instâncias inviáveis não são diagnosticadas | Torna explícita a regra de contiguidade e localiza a causa das 2 instâncias inviáveis (janela menor que a soma dos blocos) |
| Bahmani et al. (2022) | Otimização do agendamento de flexibilidade industrial a partir de um formato de dados genérico (Energy Flexibility Data Model) | O formato é a entrada da otimização; não há validação semântica das restrições antes de otimizar | Valida as restrições antes da simulação e compara com uma validação equivalente em código |

**Leitura crítica.** Os trabalhos de flexibilidade tratam os dados de entrada como corretos. O nosso Experimento II mostra que mesmo um benchmark publicado tem regras implícitas e instâncias inviáveis. Validar a entrada é uma etapa que costuma ficar fora desses estudos.

## 3. Ontologias de energia e validação semântica

| Trabalho | O que fez | Limitação | Diferencial do projeto |
|---|---|---|---|
| ETSI TS 103 410-1 (SAREF4ENER) | Ontologia padrão para descrever a flexibilidade de dispositivos (`PowerProfile`, `PowerSequence`, `Slot`), baseada em EEBus/Energy@Home e nas normas SPINE e S2 | Pensada para eletrodomésticos e gestão de energia; não modela precedências com defasagem entre tarefas industriais | Usa `PowerSequence` e `Slot` e cria uma extensão local para as precedências industriais |
| W3C SHACL (Knublauch e Kontokostas, 2017) | Linguagem padrão para declarar e validar restrições sobre grafos RDF | É a ferramenta, não uma avaliação de uso | Mede, com injeção de erros e um controle em Python, o que a validação declarada acrescenta |
| Mulayim et al. (2026) | Levantou os requisitos de informação de resposta à demanda em edifícios comerciais e avaliou a cobertura de Brick, DELTA, EFOnt e CIM | Foco em edifícios, avaliação de cobertura manual; não trata indústria nem validação automática | Avalia empiricamente a preservação de restrições industriais, com métricas de detecção e localização |

**Leitura crítica.** Os trabalhos com ontologias de energia costumam avaliar cobertura de conceitos ou propor arquiteturas. É raro medir quantitativamente o que a representação semântica evita na prática. O nosso projeto faz essa medição e compara com uma alternativa sem semântica que tem as mesmas regras.

## 4. Conhecimento do domínio na seleção de variáveis

| Trabalho | O que fez | Limitação | Diferencial do projeto |
|---|---|---|---|
| Brandmeier e Franke (2016) | Usou ontologias para classificar medidas de eficiência energética e guiar usuários iniciantes na escolha de medidas, com demonstração em acionamentos elétricos e bombas | Sistema de apoio baseado em regras do especialista, sem aprendizado a partir de dados nem avaliação quantitativa do acerto | Combina a relação semântica com aprendizado supervisionado em 8.832 auditorias e mede o ganho contra controles |
| Groves (2013) | Propôs usar relações conhecidas entre variáveis para guiar a seleção de variáveis e evitar sobreajuste | Arcabouço geral, sem avaliação no domínio de energia | Aplica a ideia a um caso concreto e testa contra controles aleatório, estatístico e placebo |
| Ringsquandl et al. (2015) | Usou uma ontologia de automação industrial para selecionar variáveis por raciocínio, com bons resultados em dados simulados e amostra pequena | Dados simulados; avaliação real ficou como trabalho futuro | Usa dados reais (8.832 auditorias) e valida em setores não vistos |

**Leitura crítica.** Esses trabalhos defendem que o conhecimento do domínio reduz o espaço de variáveis sem perder desempenho. O nosso resultado confirma isso de forma moderada: a escolha pelo significado empata com a escolha estatística e com o uso de todas as variáveis, ou seja, ganha em parcimônia, não em desempenho.

## Referências conferidas

- Anderson, S. T.; Newell, R. G. (2004). Information programs for technology adoption: the case of energy-efficiency audits. *Resource and Energy Economics*, 26(1), 27–50. https://ideas.repec.org/a/eee/resene/v26y2004i1p27-50.html
- Bahmani, R. et al. (2022). Optimal industrial flexibility scheduling based on generic data format. *Energy Informatics*, 5, 26. https://doi.org/10.1186/s42162-022-00198-4
- Blass, V.; Corbett, C. J.; Delmas, M. A.; Muthulingam, S. (2014). Top management and the adoption of energy efficiency practices: evidence from small and medium-sized manufacturing firms in the US. *Energy*, 65, 560–571. https://ideas.repec.org/a/eee/energy/v65y2014icp560-571.html
- Brandmeier, M. A.; Franke, J. (2016). Ontology-based user guidance for energy efficiency optimization measures. *Proceedings of the 6th International Conference on Industrial Engineering and Operations Management (IEOM)*, Kuala Lumpur, 1649–1657. https://cris.fau.de/publications/122017544
- ETSI (2024). TS 103 410-1 V1.2.1 — SmartM2M; Extension to SAREF; Part 1: Energy Domain (SAREF4ENER). https://saref.etsi.org/saref4ener/v1.2.1
- Groves, W. (2013). Using domain knowledge to systematically guide feature selection. *Proceedings of IJCAI 2013*. https://ijcai.org/proceedings/2013/494
- Ludwig, N.; Barth, L.; Wagner, D.; Hagenmeyer, V. (2019). Industrial demand-side flexibility: a benchmark data set. *Proceedings of ACM e-Energy '19*. https://i11www.iti.kit.edu/extra/publications/lbwh-idsfa-19.pdf
- Miera, K.; Abbas, A. I.; Nimbalkar, S.; Wenning, T. (2025). Analysis of US Industrial Assessment Centers (IACs) implementation. *Energy*, 315, 134415. https://impact.ornl.gov/en/publications/analysis-of-us-industrial-assessment-centers-iacs-implementation/
- Mulayim, O. B. et al. (2026). Semantic technologies in practical demand response: an information requirement-based roadmap. *Proceedings of ACM e-Energy '26*. https://arxiv.org/abs/2509.01459
- Ringsquandl, M.; Lamparter, S.; Brandt, S.; Hubauer, T.; Lepratti, R. (2015). Semantic-guided feature selection for industrial automation systems. *ISWC 2015*, LNCS 9367, 225–240. https://researchr.org/publication/RingsquandlLBHL15
- Sarswatula, S. A.; Pugh, T.; Prabhu, V. (2022). Modeling energy consumption using machine learning. *Frontiers in Manufacturing Technology*, 2. https://www.frontiersin.org/articles/10.3389/fmtec.2022.855208/full

Referências de método (padrão, citadas no artigo): Breiman (2001) Random Forests, *Machine Learning* 45(1); Chen e Guestrin (2016) XGBoost, *KDD '16*; Knublauch e Kontokostas (2017) SHACL, W3C Recommendation; Zaharia et al. (2018) MLflow, *IEEE Data Engineering Bulletin* 41(4); Davison e Hinkley (1997) *Bootstrap Methods and their Application*, Cambridge University Press.
