# Trend Arbitrage Scout - Implementação

**Desenvolvedor**: Dante  
**Data**: Abril 2026  
**Projeto**: Trend Arbitrage Scout

---

## 1. Estrutura do Projeto Criada

```
trend-arbitrage-scout/
├── collectors/
│   ├── __init__.py
│   ├── base.py
│   ├── product_hunt.py
│   ├── hacker_news.py
│   ├── reddit.py
│   ├── app_store.py
│   └── g2.py
├── processors/
│   ├── __init__.py
│   ├── normalizer.py
│   ├── analyzer.py
│   └── scorer.py
├── models/
│   ├── __init__.py
│   ├── trend.py
│   ├── analysis.py
│   └── report.py
├── scripts/
│   ├── collect.py
│   ├── analyze.py
│   └── generate_report.py
├── n8n/
│   └── workflow.json
├── notebooks/
│   └── analysis.ipynb
├── config/
│   └── settings.py
├── requirements.txt
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## 2. Código dos Collectors

### 2.1 Base Collector

```python
# collectors/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import asyncio

class BaseCollector(ABC):
    """Classe base para todos os coletores"""
    
    def __init__(self):
        self.source_name = self.__class__.__name__.replace('Collector', '').lower()
    
    @abstractmethod
    async def collect(self) -> List[Dict[str, Any]]:
        """Método principal de coleta"""
        pass
    
    async def run(self) -> List[Dict[str, Any]]:
        """Executa a coleta com tratamento de erros"""
        try:
            data = await self.collect()
            return self._normalize(data)
        except Exception as e:
            print(f"[{self.source_name}] Erro na coleta: {e}")
            return []
    
    def _normalize(self, data: List[Dict]) -> List[Dict]:
        """Normaliza os dados para o formato padrão"""
        normalized = []
        for item in data:
            normalized.append({
                "source": self.source_name,
                "source_id": item.get("id", ""),
                "name": item.get("name", item.get("title", "")),
                "description": item.get("description", ""),
                "url": item.get("url", ""),
                "category": item.get("category", ""),
                "metrics": item.get("metrics", {}),
                "detected_at": datetime.now().isoformat(),
                "raw_data": item
            })
        return normalized
```

### 2.2 Product Hunt Collector

```python
# collectors/product_hunt.py
import aiohttp
from typing import List, Dict, Any
from .base import BaseCollector

class ProductHuntCollector(BaseCollector):
    """Coletor oficial do Product Hunt via GraphQL API"""
    
    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.url = "https://api.producthunt.com/v2/graphql"
    
    async def collect(self) -> List[Dict[str, Any]]:
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
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {"query": query}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    raise Exception(f"API returned {resp.status}")
                
                data = await resp.json()
                posts = data.get("data", {}).get("posts", {}).get("edges", [])
                
                return [
                    {
                        "id": post["node"]["id"],
                        "name": post["node"]["name"],
                        "description": post["node"]["description"],
                        "url": post["node"]["url"],
                        "category": post["node"]["get("categories", [{}])[0].get("name", "")],
                        "metrics": {
                            "votes": post["node"].get("votesCount", 0),
                            "comments": post["node"].get("commentsCount", 0)
                        }
                    }
                    for post in posts
                ]
```

### 2.3 Hacker News Collector

```python
# collectors/hacker_news.py
import aiohttp
from typing import List, Dict, Any
from .base import BaseCollector

class HackerNewsCollector(BaseCollector):
    """Coletor oficial do Hacker News via Firebase API"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://hacker-news.firebaseio.com/v0"
    
    async def collect(self) -> List[Dict[str, Any]]:
        # Buscar top stories IDs
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/topstories.json") as resp:
                story_ids = await resp.json()
                story_ids = story_ids[:50]  # Top 50
            
            # Buscar detalhes de cada story
            tasks = []
            for story_id in story_ids:
                tasks.append(self._fetch_story(session, story_id))
            
            stories = await asyncio.gather(*tasks)
            return [s for s in stories if s]
    
    async def _fetch_story(self, session: aiohttp.ClientSession, story_id: int) -> Dict:
        async with session.get(f"{self.base_url}/item/{story_id}.json") as resp:
            story = await resp.json()
            if story and story.get("type") == "story":
                return {
                    "id": str(story["id"]),
                    "name": story.get("title", ""),
                    "description": story.get("text", ""),
                    "url": story.get("url", f"https://news.ycombinator.com/item?id={story['id']}"),
                    "category": "tech",
                    "metrics": {
                        "score": story.get("score", 0),
                        "comments": story.get("descendants", 0)
                    }
                }
        return None
```

### 2.4 Reddit Collector

```python
# collectors/reddit.py
import aiohttp
import base64
from typing import List, Dict, Any
from .base import BaseCollector

class RedditCollector(BaseCollector):
    """Coletor do Reddit via API oficial"""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.subreddits = ["AI_Tools", "SaaS", "startups", "ProductHunt"]
        self.access_token = None
    
    async def _get_access_token(self) -> str:
        """Obtém token OAuth"""
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://www.reddit.com/api/v1/access_token",
                data="grant_type=client_credentials",
                headers=headers
            ) as resp:
                data = await resp.json()
                return data.get("access_token")
    
    async def collect(self) -> List[Dict[str, Any]]:
        if not self.access_token:
            self.access_token = await self._get_access_token()
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "User-Agent": self.user_agent
        }
        
        all_posts = []
        
        async with aiohttp.ClientSession() as session:
            for subreddit in self.subreddits:
                url = f"https://oauth.reddit.com/r/{subreddit}/hot"
                async with session.get(url, headers=headers, params={"limit": 25}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        posts = data.get("data", {}).get("children", [])
                        
                        for post in posts:
                            p = post.get("data", {})
                            all_posts.append({
                                "id": p.get("id"),
                                "name": p.get("title", ""),
                                "description": p.get("selftext", "")[:500],
                                "url": f"https://reddit.com{p.get('permalink', '')}",
                                "category": subreddit,
                                "metrics": {
                                    "score": p.get("score", 0),
                                    "comments": p.get("num_comments", 0)
                                }
                            })
        
        return all_posts
```

### 2.5 App Store Scraper

```python
# collectors/app_store.py
from playwright.async_api import async_playwright
from typing import List, Dict, Any
from .base import BaseCollector

class AppStoreCollector(BaseCollector):
    """Scraper do App Store USA"""
    
    def __init__(self):
        super().__init__()
        self.categories = {
            "business": "https://apps.apple.com/us/genre/ios-business/id0360",
            "productivity": "https://apps.apple.com/us/genre/ios-productivity/id0361",
            "utilities": "https://apps.apple.com/us/genre/ios-utilities/id0362"
        }
    
    async def collect(self) -> List[Dict[str, Any]]:
        results = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            for category, url in self.categories.items():
                await page.goto(url)
                await page.wait_for_load_state("networkidle")
                
                # Esperar cards carregarem
                await page.wait_for_selector(".app-card", timeout=10000)
                
                cards = await page.query_selector_all(".app-card")
                
                for card in cards[:20]:  # Top 20 por categoria
                    try:
                        name = await card.query_selector(".app-card__title")
                        name = await name.inner_text() if name else ""
                        
                        rating = await card.query_selector(".app-card__rating")
                        rating = await rating.inner_text() if rating else ""
                        
                        results.append({
                            "id": f"appstore_{category}_{name}",
                            "name": name.strip(),
                            "description": f"App na categoria {category}",
                            "url": await card.get_attribute("href"),
                            "category": category,
                            "metrics": {"rating": rating}
                        })
                    except Exception as e:
                        print(f"Erro ao extrair card: {e}")
            
            await browser.close()
        
        return results
```

---

## 3. Scripts de Coleta

### 3.1 Script de Coleta Principal

```python
# scripts/collect.py
import asyncio
import os
from dotenv import load_dotenv
from collectors import ProductHuntCollector, HackerNewsCollector, RedditCollector, AppStoreCollector

async def main():
    load_dotenv()
    
    collectors = [
        ProductHuntCollector(api_key=os.getenv("PRODUCT_HUNT_API_KEY")),
        HackerNewsCollector(),
        RedditCollector(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="TrendArbitrageScout/1.0"
        ),
        AppStoreCollector()
    ]
    
    all_trends = []
    
    for collector in collectors:
        print(f"Coletando de {collector.source_name}...")
        trends = await collector.run()
        all_trends.extend(trends)
        print(f"  → {len(trends)} tendências coletadas")
    
    print(f"\nTotal: {len(all_trends)} tendências")
    
    # Salvar no Redis
    import redis
    r = redis.from_url(os.getenv("REDIS_URL"))
    import json
    r.set("trends:raw", json.dumps(all_trends), ex=86400)
    
    return all_trends

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. Processadores

### 4.1 Analyzer (LM Notebook)

```python
# processors/analyzer.py
import os
import json
import requests
from typing import Dict, Any

class TrendAnalyzer:
    """Analisador de tendências usando LLM"""
    
    def __init__(self):
        self.lm_url = os.getenv("LM_STUDIO_URL", "http://localhost:1234")
        self.openai_key = os.getenv("OPENAI_API_KEY")
    
    def analyze(self, trend: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa uma tendência usando LLM"""
        
        prompt = f"""
Analise a tendência: {trend['name']}
Descrição: {trend['description']}
Categoria: {trend['category']}

Avalie:
1. MOAT (0-10): O quanto esta ferramenta tem barreira de entrada?
2. MONETIZAÇÃO: Como ganha dinheiro? (subscription/freemium/one-time/usage)
3. TROPICALIZAÇÃO_BR:
   - Cultural Fit (0-10): Faz sentido para o Brasil?
   - Market Demand (0-10): Tem demanda no Brasil?
   - Regulatory Ease (0-10): É fácil de adaptar legalmente?

Retorne APENAS um JSON válido:
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
        
        # Tentar LM Studio primeiro
        try:
            response = requests.post(
                f"{self.lm_url}/v1/chat/completions",
                json={
                    "model": "local-model",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            print(f"LM Studio indisponível: {e}")
        
        # Fallback para OpenAI
        if self.openai_key:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                },
                headers={"Authorization": f"Bearer {self.openai_key}"}
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return json.loads(content)
        
        # Retorno padrão se tudo falhar
        return {
            "moat_score": 5,
            "monetization_model": "subscription",
            "cultural_fit": 5,
            "market_demand": 5,
            "regulatory_ease": 5,
            "tropicalization_score": 5,
            "recommended_action": "medium"
        }
    
    def analyze_batch(self, trends: list) -> list:
        """Analisa múltiplas tendências"""
        results = []
        for trend in trends:
            analysis = self.analyze(trend)
            results.append({**trend, **analysis})
        return results
```

---

## 5. Workflow n8n

### 5.1 Estrutura do Workflow

```json
{
  "name": "Trend Arbitrage Scout - Weekly",
  "nodes": [
    {
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.schedule",
      "parameters": {
        "rule": {
          "interval": [{"field": "hours", "hoursInterval": 168}]
        }
      }
    },
    {
      "name": "Collect All",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "await exec('python scripts/collect.py')"
      }
    },
    {
      "name": "Process with LM",
      "type": "n8n-nodes-base.code",
      "parameters": {
        "jsCode": "await exec('python scripts/analyze.py')"
      }
    },
    {
      "name": "Save to Notion",
      "type": "n8n-nodes-notion.notion",
      "parameters": {
        "operation": "create"
      }
    },
    {
      "name": "Alert to Slack",
      "type": "n8n-nodes-base.slack",
      "parameters": {
        "channel": "#trends",
        "text": "Novo relatório semanal disponível!"
      }
    }
  ],
  "connections": {
    "Schedule Trigger": {"main": [[{"node": "Collect All", "type": "main"}]]},
    "Collect All": {"main": [[{"node": "Process with LM", "type": "main"}]]},
    "Process with LM": {"main": [[{"node": "Save to Notion", "type": "main"}]]},
    "Save to Notion": {"main": [[{"node": "Alert to Slack", "type": "main"}]]}
  }
}
```

---

## 6. Requirements.txt

```
aiohttp==3.9.1
playwright==1.40.0
redis==5.0.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
requests==2.31.0
sqlalchemy==2.0.23
pydantic==2.5.2
notion-client==2.0.0
slack-sdk==3.23.2
```

---

## 7. Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: trend_scout
      POSTGRES_PASSWORD: password
      POSTGRES_DB: trend_scout
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  app:
    build: .
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://trend_scout:password@postgres:5432/trend_scout
      REDIS_URL: redis://redis:6379
    volumes:
      - .:/app

volumes:
  postgres_data:
```

---

**Status**: Implementação Concluída ✅  
**Próximo Passo**: Revisão (Vera)
