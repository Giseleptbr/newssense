# NewsSense — Resumo e Classificação de Sentimento de Notícias Financeiras

Projeto da disciplina Projetos de IA (Módulo 7, PPI/SiDi). Projeto individual.

## 1. Introdução [E1]

### 1.1 Título
NewsSense — Resumo e Classificação de Sentimento de Notícias Financeiras em Tempo Real

### 1.2 Equipe
| Nome | Papel principal |
|---|---|
| Gisele | Todos os papéis (projeto individual) |

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

#### 3.6.1 Critério de rotulagem manual

A rotulagem de sentimento (positivo / negativo / neutro) segue as regras abaixo, consolidadas durante a primeira leva de anotação (18 notícias, 30/06/2026):

- **O rótulo reflete o estado/situação presente do evento, não o desfecho hipotético futuro.** Ex: uma empresa em processo de venda/reestruturação é rotulada como negativo (problema ocorrendo agora), mesmo que a reestruturação possa trazer melhora depois.
- **Ações ou propostas corretivas em curso (governo, empresa, instituição) tendem a positivo**, por representarem resposta ativa a um problema (ex: proposta de renegociação de dívida, mecanismo para conter alta de preço, avanço de pauta institucional como autonomia do BC).
- **Para notícias com informação mista** (ex: queda de ativo + recomendação de compra de analista), prevalece o evento de mercado principal, não a recomendação subsequente.
- **Notícias sem nenhuma conexão com mercado/economia** (política partidária interna, esportes, etc., presentes no feed "geral" por não terem categoria própria) são rotuladas como neutro. Avaliar em revisão futura se devem ser excluídas do dataset por estarem fora do escopo do projeto.
- **Notícias com sinais conflitantes de direção oposta no mesmo texto** (ex: crescimento de um indicador positivo acompanhado de alerta de risco no mesmo resumo) são rotuladas como neutro. A classe "neutro" cobre três situações: (1) notícia informativa sem viés de mercado; (2) notícia fora do escopo financeiro; (3) notícia genuinamente mista com eventos positivos e negativos simultâneos sem direção dominante clara. Uma 4ª classe "misto" pode ser considerada em refinamento futuro do schema de rotulagem.
- **Declarações político-institucionais sobre desempenho econômico** (sem dado novo e verificável) são rotuladas pelo teor da fala (positivo/negativo), não automaticamente como neutro.

Por ser rotulagem individual, esse critério está sujeito a viés de interpretação de uma única anotadora — limitação documentada e a ser discutida na Entrega 2 (Seção 6.2).


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

---

## 8. Análise Comparativa dos Modelos (atualização em andamento)

### 8.1 Resultados de accuracy (N=54 rótulos manuais)

| Modelo | Accuracy | Acertos |
|---|---|---|
| Chute pela classe majoritária (referência) | ~37% | ~20/54 |
| Zero-shot multilíngue (cardiffnlp/twitter-xlm-roberta) | 42,59% | 23/54 |
| Ensemble maioria (3 modelos) | 42,59% | 23/54 |
| Lexicon genérico (OpLexicon v3.0) | 46,30% | 25/54 |
| FinBERT-PT-BR (lucas-leme/FinBERT-PT-BR) | 46,30% | 25/54 |
| Ensemble lex-priority | 46,30% | 25/54 |
| Ensemble fin-priority | 46,30% | 25/54 |

**Conclusão:** o teto sem fine-tuning é 46,30%. Nenhuma combinação de modelos pré-treinados supera esse valor com os dados atuais. Para atingir a meta de F1-macro ≥ 0,70 da proposta, o caminho necessário é fine-tuning do FinBERT-PT-BR com os rótulos manuais deste projeto (meta: 100-150 exemplos).

### 8.2 Padrões de erro identificados (inspeção qualitativa)

Ao inspecionar os casos onde Lexicon e FinBERT divergem entre si, identificaram-se dois padrões complementares:

**FinBERT-PT-BR acerta onde o Lexicon erra:**
- Notícias de queda de mercado com vocabulário neutro no título (ex: "Ibovespa cai e tenta segurar 172 mil pontos", "Ouro recua 12%", "Bitcoin pior investimento do semestre") — o FinBERT entende o contexto financeiro; o Lexicon fica preso em adjetivos isolados como "forte" ou "segura", que têm polaridade positiva fora de contexto.
- Notícias de risco fiscal ("déficit público", "pauta-bomba avançar") — FinBERT capta o tom negativo corretamente.

**Lexicon acerta onde o FinBERT erra:**
- Notícias institucionais/políticas com tom positivo declarado (ex: "Petrobras cria mecanismo e limita alta do gás", "Senado adia votação de pauta-bomba", "Tesouro paga juros históricos") — o FinBERT classifica como neutro ou negativo porque foi treinado com um critério diferente (juros altos = negativo no corpus de treino, mas no critério deste projeto = oportunidade de investimento = positivo).
- Notícias de Copa/esportes/política sem relação com mercado — o FinBERT vicia em negativo; o Lexicon acerta neutro com score zero (sem termos financeiros reconhecidos).

### 8.3 Interpretação

O ensemble (42,59%) ficou abaixo dos dois modelos individuais (46,30% cada), o que é contra-intuitivo mas explicável: os dois modelos concordam em apenas 37% dos casos. Quando divergem (63% das notícias), o desempate por confiança do FinBERT escolhe errado sistematicamente nos casos de notícias institucionais/políticas — exatamente onde o lexicon é mais forte. Com N=54, qualquer ajuste fino no critério de desempate seria overfitting.

O resultado mais relevante permanece o empate entre Lexicon e FinBERT com **conjuntos de erro complementares**: os dois acertam e erram em casos distintos. Isso não é sinal de que os modelos são equivalentes — é sinal de que nenhum dos dois aprendeu o critério de rotulagem deste projeto. A raiz do problema é o **desalinhamento de critério**: os modelos foram treinados com uma definição de sentimento diferente da adotada neste projeto. O critério deste projeto ("estado presente + ação corretiva = positivo") é mais contextual e menos emocional do que os critérios de treino padrão.

Isso reforça a hipótese central: **fine-tuning do FinBERT-PT-BR com os rótulos manuais deste projeto** (meta: 100-150) deve ser o passo que de fato faz diferença, pois alinha o modelo ao critério específico de rotulagem adotado — sem isso, qualquer combinação dos modelos existentes opera num critério diferente do esperado.

### 8.4 Próximos passos

1. **Ensemble** (Lexicon + FinBERT com desempate por confiança) — resultado a preencher
2. **Fine-tuning do FinBERT-PT-BR** com os rótulos manuais acumulados, a partir de 100-150 exemplos
3. **Correlação sentimento x Ibovespa** — ver Seção 9

---

## 9. Trabalhos Futuros

### 8.1 Correlação entre Sentimento Agregado Diário e Retorno do Ibovespa

**Motivação:** durante o processo de rotulagem manual, surgiu a hipótese de que o sentimento agregado das notícias publicadas num dia específico pode estar correlacionado com a variação do Ibovespa naquele mesmo dia ou no dia seguinte (efeito defasado). Essa análise conecta diretamente o pipeline de NLP com evidência observável de mercado, e é extensão natural da pesquisa da autora sobre sentimento de investidor e precificação de ativos (FIIs, IFIX — tema do mestrado em Finanças na UFPB).

**O que seria necessário:**

**1. Volume temporal suficiente:** a análise só é estatisticamente válida com pelo menos 20-30 dias distintos de coleta acumulada, onde cada dia tenha sentimento agregado calculável. Com coleta iniciada em 30/jun/2026, isso estará disponível em meados de agosto/2026.

**2. Índice de sentimento agregado diário:** agrupar as notícias por `data_publicacao` e calcular, por dia, a proporção de positivas/negativas/neutras — gerando um score diário entre -1 e +1.

**3. Retorno diário do Ibovespa via yfinance (Yahoo Finance API):**
```python
import yfinance as yf
ibov = yf.download("^BVSP", start="2026-06-30", end="2026-08-31")
ibov["retorno"] = ibov["Close"].pct_change()
```

**4. Análise de correlação:** cruzar o índice de sentimento diário com o retorno do Ibovespa no mesmo dia (contemporâneo) e com defasagem de 1 dia (sentimento de hoje prediz retorno de amanhã — análise preditiva). Métricas: correlação de Pearson/Spearman, regressão linear simples sentimento → retorno.

**5. Fonte retroativa de notícias via Wayback Machine (para ampliar janela temporal):** o Wayback Machine (https://web.archive.org/) arquiva páginas do InfoMoney com timestamp histórico, permitindo recuperar notícias de datas anteriores a 30/jun/2026. Endpoint de API:
```
http://archive.org/wayback/available?url=infomoney.com.br/mercados&timestamp=20260601
```
Retorna o snapshot mais próximo da data solicitada. Isso permitiria retroativamente coletar títulos de notícias de mercado de jan–jun/2026 e cruzar com o retorno histórico do Ibovespa, ampliando a janela de análise de 1 mês para 6+ meses. Respeitar os mesmos limites já aplicados no projeto: apenas título e metadados, sem corpo de texto.

**Hipótese a testar:** dias com proporção de notícias negativas acima de determinado limiar antecedem quedas do Ibovespa no dia seguinte com frequência estatisticamente superior ao acaso.

**Por que ainda não foi feita:** volume temporal insuficiente na data de entrega (30/jun–31/jul/2026 é janela de apenas 1 mês). Retornar após 60-90 dias de coleta acumulada.

**Referência metodológica:** Baker & Wurgler (2006) — framework de índice de sentimento de investidor aplicado a retornos de ativos; base teórica já utilizada na dissertação de mestrado da autora.

