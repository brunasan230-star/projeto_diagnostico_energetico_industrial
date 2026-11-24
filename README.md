# Conhecimento setorial e representação semântica no diagnóstico energético industrial

## Autoras

**Bruna Santos**  
Departamento de Engenharia Industrial – PUC-Rio  
Rio de Janeiro – RJ – Brasil  
E-mail: brunasantos230@outlook.com

**Luisa Millen Compasso**  
Departamento de Engenharia Industrial – PUC-Rio  
Rio de Janeiro – RJ – Brasil  
E-mail: luisamillenc@gmail.co

## Resumo

Este trabalho avalia duas etapas do diagnóstico energético industrial.

Na primeira, classificadores Random Forest, XGBoost e regressão logística priorizam famílias de intervenção em 8.832 auditorias do ITAC, com e sem o perfil setorial de uso de eletricidade do MECS. Em setores não vistos no treino, o perfil escolhido pela relação semântica com cada família elevou a macro-AP em 0,013 a 0,024, e um controle placebo confirmou que o ganho vem do perfil verdadeiro. A escolha semântica ficou equivalente à seleção estatística e ao uso de todas as variáveis, com diferenças de no máximo 0,004.

Na segunda, tarefas do benchmark KIT foram preparadas para simulação por uma rota direta, pela mesma rota com regras em Python e por uma rota semântica com SHACL. As três preservaram as restrições; sem regras, 45% dos erros injetados passaram sem detecção, enquanto as duas implementações de regras detectaram todos. A validação revelou duas instâncias inviáveis na base publicada.

## 1. Estrutura do repositório

| Diretório ou arquivo | Descrição |
|---|---|
| `experimento_I/` | Q1: notebook final, dados, saídas e log do MLflow. |
| `experimento_II/` | Q2: notebook final, rotas de implementação, saídas e log do MLflow. |
| `trabalhos_relacionados.md` | Levantamento bibliográfico com análise crítica e referências conferidas. |
| `auditoria_csv_itac.md` | Conferência dos filtros aplicados ao CSV integrado do ITAC. |

### Experimento I (Q1)

Contém os materiais relacionados à avaliação do conhecimento setorial na priorização de famílias de intervenção:

- Notebook final;
- Bases de dados;
- Resultados e saídas do experimento;
- Registros de execução do MLflow.

### Experimento II (Q2)

Contém os materiais relacionados à avaliação da representação semântica e à validação de restrições:

- Notebook final;
- `kit_rotas.py`: implementação das rotas de preparação para simulação;
- `regras_python.py`: implementação das regras de validação em Python;
- Resultados e saídas do experimento;
- Registros de execução do MLflow.

**Importante:** a base de dados do KIT deve ser descompactada no seguinte diretório:

```text
experimento_II/data/dataset/archive/
```

## 2. Instalação das dependências

Para instalar as bibliotecas necessárias à execução dos experimentos, utilize:

```bash
pip install mlflow scikit-learn xgboost rdflib pyshacl
```

## 3. Monitoramento dos experimentos com MLflow

O MLflow é utilizado para registrar e acompanhar as execuções dos experimentos.

Para acessar a interface de visualização, execute o comando abaixo dentro da pasta do respectivo experimento:

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Após a inicialização, acesse a interface pelo navegador:

[http://localhost:5000](http://localhost:5000)

## 4. Tempo estimado de execução

| Experimento | Tempo estimado |
|---|---:|
| Experimento I (Q1) | 40 minutos |
| Experimento II (Q2) | 2 horas |
| Validação SHACL das 1.764 instâncias (parte do Q2) | 1 hora e 45 minutos |

Os tempos são aproximados e podem variar conforme a configuração de hardware e o ambiente computacional utilizado.
