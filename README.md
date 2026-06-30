# NewsSense — Resumo e Classificação de Sentimento de Notícias Financeiras

Projeto da disciplina Projetos de IA (Módulo 7, PPI/SiDi). Projeto individual.

## 1. Introdução [E1]

### 1.1 Título
NewsSense — Resumo e Classificação de Sentimento de Notícias Financeiras em Tempo Real

### 1.2 Equipe
| Nome | Papel principal |
|---|---|
| Gisele | Todos os papéis (projeto individual, aprovado pelo instrutor) |

### 1.3 Contexto e motivação
Investidores de varejo acompanham dezenas de notícias financeiras diariamente, mas raramente têm tempo de ler cada matéria por completo para decidir sua relevância. Um sistema que resume automaticamente e classifica o tom (positivo/negativo/neutro) de uma notícia em relação ao mercado permite triagem rápida, reduzindo a sobrecarga informacional e apoiando decisões de acompanhamento mais ágeis.

### 1.4 Problema / pergunta de pesquisa
É possível, a partir do título e resumo de uma notícia financeira coletada via RSS, gerar automaticamente um resumo curto e uma classificação de sentimento (positivo/negativo/neutro) que ajude o investidor a decidir rapidamente se vale a pena ler a matéria completa?

### 1.5 Hipótese
Um classificador de sentimento ajustado ao vocabulário financeiro em português supera, em concordância com julgamento humano, uma abordagem de baseline baseada em lexicon genérico (sem adaptação ao domínio).

### 1.6 Objetivos
1. Construir pipeline de coleta contínua de notícias via RSS de múltiplas fontes financeiras brasileiras.
2. Realizar EDA do volume e distribuição de notícias por categoria/fonte.
3. Implementar resumo extractive das notícias coletadas.
4. Treinar/ajustar classificador de sentimento financeiro em português, comparado a baseline (lexicon genérico).
5. Validar com amostra rotulada manualmente.
6. Entregar painel simples de leitura rápida (notícia + resumo + sentimento).

## 2. Dados

### 2.1 Fonte e licença [E1]
Feeds RSS públicos de portais de notícias financeiras brasileiros:
- InfoMoney: `/feed/`, `/mercados/feed/`, `/onde-investir/feed/`, `/economia/feed/`
- [TODO] avaliar inclusão de Valor Econômico (`/rss`) e outras fontes conforme disponibilidade

Apenas título, link, data e resumo curto (já fornecido pelo feed, com HTML removido) são armazenados — não o corpo integral das matérias.

### 2.2 Volume e formato [E1]
Coleta incremental (execução manual/agendada), deduplicada por link. Estimativa de 30-80 itens/dia somando as fontes ativas. Armazenado em `data/raw/noticias.csv`.

Status atual: **10 notícias coletadas** (30/jun/2026, primeira execução de teste).

### 2.3 Variáveis principais [E1]
| Variável | Tipo | Descrição |
|---|---|---|
| fonte | categórica | Feed de origem (ex: infomoney_mercados) |
| categoria | categórica | Mercados, Economia, Onde Investir, Geral |
| titulo | texto | Título da notícia |
| resumo_rss | texto | Resumo curto do feed, HTML removido |
| link | texto | URL da matéria completa |
| data_publicacao | data | Timestamp de publicação original |
| coletado_em | data | Timestamp da coleta local |

### 2.4 Riscos de dados [E1]
- Resumo do RSS pode ser curto demais para captar nuance de sentimento em alguns casos.
- URLs de feed podem mudar ao longo do projeto (mitigado por múltiplas fontes).
- Sem PII; sem dados sensíveis.

### 2.5 Pré-processamento aplicado [E2]
[TODO Entrega 2]

### 2.6 Ética e privacidade [E1]
Sem dados pessoais. Uso restrito a título e resumo curto já publicamente distribuído via RSS, sem reprodução de texto integral, respeitando direitos autorais dos veículos.

## 3. Metodologia

### 3.1 Abordagem [E1]
NLP: resumo extractive (seleção de frases-chave) + classificação de sentimento supervisionada (texto curto, 3 classes: positivo/negativo/neutro).

### 3.2 Stack técnica [E1]
Python 3.11, `feedparser` (coleta RSS), pandas, scikit-learn, NLTK/spaCy (PT-BR), modelo de sentimento (BERTimbau fine-tuned ou lexicon adaptado como baseline), MLflow para tracking, venv para ambiente.

### 3.3 Baselines [E1]
Lexicon de sentimento genérico em português (ex: SentiLex-PT ou OpLexicon), sem ajuste de domínio financeiro.

### 3.4 Pipeline [E2]
[TODO Entrega 2]

### 3.5 Modelos comparados [E2]
[TODO Entrega 2]

### 3.6 Protocolo de validação [E1]
Amostra de ~100-150 notícias rotuladas manualmente como verdade de referência; split treino/validação respeitando ordem temporal de coleta (sem vazamento futuro→passado).

### 3.7 Métricas e critérios de sucesso [E1]
- F1-macro ≥ 0.70 nas 3 classes de sentimento
- Accuracy do modelo ajustado superior ao baseline lexicon em pelo menos 10 pontos percentuais
- Resumo extractive avaliado qualitativamente (legibilidade e fidelidade) em amostra de 20 casos

## 4. Cronograma [E1: planejado]

| Semana | Período | Atividade | Status |
|---|---|---|---|
| 1 | 30/jun – 06/jul | Pipeline RSS multi-fonte + início da coleta contínua | Em andamento |
| 2 | 07–13/jul | EDA + rotulagem manual da amostra + baseline lexicon | [TODO] |
| 3 | 14–20/jul | Classificador ajustado + resumo extractive | [TODO] |
| 4 | 21–27/jul | Validação, análise de erros, painel de visualização | [TODO] |
| 5 | 28–31/jul | README final, slides, ensaio de defesa | [TODO] |

## 5. Resultados [E2]
[TODO Entrega 2]

## 6. Conclusão [E2]
[TODO Entrega 2]

## 7. Reprodutibilidade

### 7.1 Requisitos
- Python 3.11+
- Ver `pyproject.toml`

### 7.2 Instalação
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install feedparser pandas scikit-learn nltk mlflow
```

### 7.3 Executar a coleta
```bash
python src/coleta_rss.py
```
Cada execução adiciona apenas notícias novas (deduplicado por link) em `data/raw/noticias.csv`.

### 7.4 Próximos comandos
[TODO Entrega 2] `make train`, `make evaluate` conforme pipeline avançar.
