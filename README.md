Conhecimento setorial e representação semântica no diagnóstico energético industrial

experimento_I/     Q1: notebook final, dados, saídas e log do MLflow
experimento_II/    Q2: notebook final, rotas (kit_rotas.py, regras_python.py), saídas e log do MLflow
                   a base do KIT deve ser descompactada em experimento_II/data/dataset/archive/
trabalhos_relacionados.md   levantamento com análise crítica e referências conferidas
auditoria_csv_itac.md       conferência dos filtros do CSV integrado

Dependências: pip install mlflow scikit-learn xgboost rdflib pyshacl
MLflow (rodar dentro de cada pasta de experimento): mlflow ui --backend-store-uri sqlite:///mlflow.db
Tempo de execução: Q1 ~40 min; Q2 ~2 h (a validação SHACL das 1.764 instâncias leva ~1h45).
