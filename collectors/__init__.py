"""
Trend Arbitrage Scout - Collectors
Automação de coleta de tendências dos EUA
Autor: Ariel (Automação)
"""

import aiohttp
import asyncio
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import json


class BaseCollector(ABC):
    """Classe base para todos os coletores"""
    
    def __init__(self):
        self.source_name = self.__class__.__name__.replace('Collector', '').lower()
    
    @abstractmethod
    async def collect(self) -> List[Dict[str, Any]]:
        """Método principal de coleta - deve ser implementado por cada coletor"""
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


class ProductHuntCollector(BaseCollector):
    """Coletor oficial do Product Hunt via GraphQL API"""
    
    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or "dev"
        self.url = "https://api.producthunt.com/v2/graphql"
    
    async def collect(self) -> List[Dict[str, Any]]:
        query = """
        {
          posts(first: 30, order: VOTES) {
            edges {
              node {
                id
                name
                description
                url
                votesCount
                commentsCount
                topics {
                  name
                }
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
                    raise Exception(f"API retornou {resp.status}")
                
                data = await resp.json()
                posts = data.get("data", {}).get("posts", {}).get("edges", [])
                
                result = []
                for post in posts:
                    node = post.get("node", {})
                    topics = node.get("topics", [])
                    category = topics[0].get("name", "general") if topics else "general"
                    
                    result.append({
                        "id": str(node.get("id")),
                        "name": node.get("name", ""),
                        "description": node.get("description", "")[:300],
                        "url": node.get("url", ""),
                        "category": category,
                        "metrics": {
                            "votes": node.get("votesCount", 0),
                            "comments": node.get("commentsCount", 0)
                        }
                    })
                
                return result


class HackerNewsCollector(BaseCollector):
    """Coletor oficial do Hacker News via Firebase API"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://hacker-news.firebaseio.com/v0"
    
    async def collect(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/topstories.json") as resp:
                story_ids = await resp.json()
                story_ids = story_ids[:30]
            
            tasks = [self._fetch_story(session, sid) for sid in story_ids]
            stories = await asyncio.gather(*tasks)
            return [s for s in stories if s]
    
    async def _fetch_story(self, session: aiohttp.ClientSession, story_id: int) -> Dict:
        async with session.get(f"{self.base_url}/item/{story_id}.json") as resp:
            story = await resp.json()
            if story and story.get("type") == "story":
                return {
                    "id": str(story["id"]),
                    "name": story.get("title", ""),
                    "description": story.get("text", "")[:300] if story.get("text") else "",
                    "url": story.get("url", f"https://news.ycombinator.com/item?id={story['id']}"),
                    "category": "tech",
                    "metrics": {
                        "score": story.get("score", 0),
                        "comments": story.get("descendants", 0)
                    }
                }
        return None


class RedditCollector(BaseCollector):
    """Coletor do Reddit via API pública (sem necessidade de OAuth)"""
    
    def __init__(self):
        super().__init__()
        self.subreddits = ["ArtificialIntelligence", "MachineLearning", "SaaS", "startups"]
        self.base_url = "https://www.reddit.com"
    
    async def collect(self) -> List[Dict[str, Any]]:
        all_posts = []
        
        async with aiohttp.ClientSession() as session:
            headers = {"User-Agent": "TrendScout/1.0"}
            
            for subreddit in self.subreddits:
                url = f"{self.base_url}/r/{subreddit}/hot.json"
                async with session.get(url, headers=headers, params={"limit": 25}) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        posts = data.get("data", {}).get("children", [])
                        
                        for post in posts:
                            p = post.get("data", {})
                            if p.get("is_self"):  # Only text posts
                                all_posts.append({
                                    "id": p.get("id"),
                                    "name": p.get("title", ""),
                                    "description": p.get("selftext", "")[:300],
                                    "url": f"https://reddit.com{p.get('permalink', '')}",
                                    "category": subreddit,
                                    "metrics": {
                                        "score": p.get("score", 0),
                                        "comments": p.get("num_comments", 0)
                                    }
                                })
        
        return all_posts


class TwitterXCollector(BaseCollector):
    """Coletor do Twitter/X via web scraping (gratuito)"""
    
    def __init__(self):
        super().__init__()
        self.search_terms = ["AI tool", "new startup", "SaaS launch", "product hunt"]
    
    async def collect(self) -> List[Dict[str, Any]]:
        # Nota: Twitter requer API paga para acesso estruturado
        # Esta é uma implementação placeholder
        # Para produção, considere alternativas como:
        # - Nitter (frontend do Twitter)
        # - BlogTwit
        # - Crawlers públicos
        
        print("[twitter] Atenção: API do Twitter é paga. Pulando coleta.")
        return []


async def run_all_collectors() -> List[Dict[str, Any]]:
    """Executa todos os coletores disponíveis"""
    
    collectors = [
        ProductHuntCollector(),
        HackerNewsCollector(),
        RedditCollector(),
    ]
    
    all_trends = []
    
    for collector in collectors:
        print(f"[Coletando] {collector.source_name}...")
        trends = await collector.run()
        all_trends.extend(trends)
        print(f"  → {len(trends)} tendências coletadas")
    
    print(f"\n[Total] {len(all_trends)} tendências coletadas")
    
    return all_trends


if __name__ == "__main__":
    trends = asyncio.run(run_all_collectors())
    
    # Salvar em arquivo JSON para uso posterior
    with open("data/raw_trends.json", "w", encoding="utf-8") as f:
        json.dump(trends, f, ensure_ascii=False, indent=2)
    
    print(f"[Salvo] {len(trends)} tendências salvas em data/raw_trends.json")
