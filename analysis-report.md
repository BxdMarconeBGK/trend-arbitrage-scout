# Trend Arbitrage Scout - Análise Técnica

**Analista**: Ariel (Automação)  
**Data**: Abril 2026  
**Projeto**: Trend Arbitrage Scout

---

## 1. Fontes de Dados Identificadas

| Fonte | Tipo | Método de Coleta | Status API |
|-------|------|------------------|------------|
| Product Hunt | API | `https://api.producthunt.com/v2/graphql` | ✅ Oficial |
| Hacker News | API | `https://hacker-news.firebaseio.com/v0/` | ✅ Oficial |
| Reddit | API | `https://www.reddit.com/dev/api/` | ✅ Oficial |
| App Store | Scraping | Playwright | 🔧 Necessário |
| Google Play | Scraping | Playwright | 🔧 Necessário |
| G2 | Scraping | Playwright | 🔧 Necessário |

## 2. Seletores e Estrutura Necessária

### 2.1 Product Hunt API GraphQL

```python
# Query para buscar produtos em alta
query = """
{
  posts(first: 50, order: VOTES) {
    edges {
      node {
        id
        name
        description
        url
        votesCount
        commentsCount
        categories {
          name
        }
        createdAt
      }
    }
  }
}
"""
```

### 2.2 Hacker News API

```python
# Endpoints necessários
TOP_STORIES = "https://hacker-news.firebaseio.com/v0/topstories.json"
ITEM = "https://hacker-news.firebaseio.com/v0/item/{id}.json"
```

### 2.3 Reddit API

```python
# Subreddits-alvo
SUBREDDITS = ["AI_Tools", "SaaS", "startups", "ProductHunt"]

# Endpoint
GET_SUBREDDIT_POSTS = "https://oauth.reddit.com/r/{subreddit}/hot"
```

### 2.4 App Store Scraping (Playwright)

```python
# URL base
APP_STORE_URL = "https://apps.apple.com/us/genre/ios-business/id0360"

# Seletores necessários
SELECTORS = {
    "app_card": "[data-testid='app-card']",
    "app_name": ".app-card__title",
    "app_rating": ".app-card__rating",
    "app_category": ".app-card__category"
}
```

## 3. Estrutura de Diretórios do Projeto

```
trend-arbitrage-scout/
├── collectors/
│   ├── __init__.py
│   ├── base.py          # Classe base
│   ├── product_hunt.py  # Coletor Product Hunt
│   ├── hacker_news.py   # Coletor Hacker News
│   ├── reddit.py        # Coletor Reddit
│   ├── app_store.py     # Coletor App Store (scraping)
│   └── g2.py            # Coletor G2
├── processors/
│   ├── __init__.py
│   ├── normalizer.py    # Normalização de dados
│   ├── analyzer.py      # Análise com LLM
│   └── scorer.py        # Cálculo de scores
├── models/
│   ├── __init__.py
│   ├── trend.py         # Modelo Trend
│   ├── analysis.py      # Modelo Analysis
│   └── report.py        # Modelo Report
├── api/
│   ├── __init__.py
│   ├── routes.py        # Endpoints
│   └── middleware.py    # Middlewares
├── scripts/
│   ├── collect.py       # Script de coleta
│   ├── analyze.py       # Script de análise
│   └── generate_report.py # Script de relatório
├── n8n/
│   └── workflow.json    # Workflow n8n
├── notebooks/
│   └── analysis.ipynb   # LM Notebook
├── tests/
│   ├── __init__.py
│   └── test_collectors.py
├── config/
│   └── settings.py     # Configurações
├── requirements.txt
├── .env.example
├── docker-compose.yml
└── README.md
```

## 4. Variáveis de Ambiente Necessárias

```bash
# APIs
PRODUCT_HUNT_API_KEY=your_key_here
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
TWITTER_BEARER_TOKEN=your_token

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/trend_scout

# Cache
REDIS_URL=redis://localhost:6379

# LM Studio
LM_STUDIO_URL=http://localhost:1234

# Integrações
NOTION_API_KEY=secret_xxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/xxx
```

## 5. Lógica de Processamento (LM Notebook)

### 5.1 Fluxo de Análise

```
1. Carregar dados raw do Redis
2. Normalizar cada tendência
3. Para cada tendência:
   a. Enviar prompt para LM com descrição
   b. Receber análise JSON
   c. Extrair scores (Moat, Monetização, Tropicalização)
4. Aplicar fórmula final
5. Salvar no PostgreSQL
6. Gerar ranking
```

### 5.2 Prompt para LM

```python
ANALYSIS_PROMPT = """
Analise a tendência: {name}
Descrição: {description}
Categoria: {category}

Avalie:
1. MOAT (0-10): O quanto esta ferramenta tem barreira de entrada?
2. MONETIZAÇÃO: Como ganha dinheiro? (subscription/freemium/one-time/usage)
3. TROPICALIZAÇÃO_BR:
   - Cultural Fit (0-10): Faz sentido para o Brasil?
   - Market Demand (0-10): Tem demanda no Brasil?
   - Regulatory Ease (0-10): É fácil de adaptar legalmente?

Retorne em JSON:
{{
  "moat_score": 0-10,
  "monetization_model": "subscription|freemium|one-time|usage",
  "cultural_fit": 0-10,
  "market_demand": 0-10,
  "regulatory_ease": 0-10,
  "tropicalization_score": 0-10,
  "recommended_action": "priority|medium|low"
}}
"""
```

## 6. Integrações MCP

### 6.1 Notion MCP

```python
# Salvar relatório no Notion
def save_to_notion(report):
    notion.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "Name": {"title": [{"text": {"content": report.title}}]},
            "Period": {"select": {"name": report.period}},
            "Trends Count": {"number": len(report.trends)},
            "Top Opportunity": {"rich_text": [{"text": {"content": report.top_opportunity}}]},
            "Date": {"date": {"start": report.generated_at}}
        }
    )
```

### 6.2 Slack MCP

```python
# Enviar alerta
def send_slack_alert(trend):
    slack.webhooks.post({
        "text": f"🔥 Nova tendência quente detectada!",
        "blocks": [
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*{trend.name}*\n{trend.description}"}
            }
        ]
    })
```

## 7. Riscos Identificados

| Risco | Probabilidade | Mitigação |
|-------|---------------|-----------|
| Rate limiting Reddit API | Alta | Implementar exponential backoff |
| Mudanças no layout App Store | Média | Usar seletores robustos (data-testid) |
| LM Studio indisponível | Média | Fallback para OpenAI API |
| Dados incompletos | Baixa | Validação com schema |

## 8. Próximos Passos

- [ ] Ariel: Implementar collectors
- [ ] Dante: Criar estrutura base do projeto
- [ ] Vera: Revisar e validar robustez

---

**Status**: Análise Completa ✅  
**Próximo Passo**: Desenvolvimento (Dante)
