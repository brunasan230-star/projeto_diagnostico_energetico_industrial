Conhecimento setorial e representação semântica no diagnóstico energético industrial


Este trabalho avalia duas etapas do diagnóstico energético industrial. Na primeira,
classificadores Random Forest, XGBoost e regressão logística priorizam famílias de in
tervenção em 8.832 auditorias do ITAC, com e sem o perfil setorial de uso de eletricidade
do MECS. Em setores não vistos no treino, o perfil escolhido pela relação semântica com
cada família elevou a macro-AP em 0,013 a 0,024, e um controle placebo confirmou que o
ganho vem do perfil verdadeiro; a escolha semântica ficou equivalente à seleção estatística
e ao uso de todas as variáveis, com diferenças de no máximo 0,004. Na segunda, tarefas
do benchmark KIT foram preparadas para simulação por uma rota direta, pela mesma
rota com regras em Python e por uma rota semântica com SHACL. As três preservaram
as restrições; sem regras, 45% dos erros injetados passaram calados, enquanto as duas
implementações de regras detectaram todos. A validação revelou duas instâncias inviáveis
na base publicada.

Para o uso do código: 

experimento_I/     Q1: notebook final, dados, saídas e log do MLflow
experimento_II/    Q2: notebook final, rotas (kit_rotas.py, regras_python.py), saídas e log do MLflow
                   a base do KIT deve ser descompactada em experimento_II/data/dataset/archive/
trabalhos_relacionados.md   levantamento com análise crítica e referências conferidas
auditoria_csv_itac.md       conferência dos filtros do CSV integrado

Dependências: pip install mlflow scikit-learn xgboost rdflib pyshacl
MLflow (rodar dentro de cada pasta de experimento): mlflow ui --backend-store-uri sqlite:///mlflow.db
Tempo de execução: Q1 ~40 min; Q2 ~2 h (a validação SHACL das 1.764 instâncias leva ~1h45).
