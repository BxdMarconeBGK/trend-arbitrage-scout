"""
Trend Arbitrage Scout - Coletor de Hacker News
Autor: Dante (Desenvolvedor)
"""

import json
import requests
from typing import List, Dict, Any
from datetime import datetime


class HackerNewsCollector:
    """Coletor de tendências do Hacker News"""
    
    def __init__(self, top_stories_url: str = "https://hacker-news.firebaseio.com/v0/topstories.json", base_url: str = "https://hacker-news.firebaseio.com/v0"):
        self.top_stories_url = top_stories_url
        self.base_url = base_url
    
    def fetch_top_stories(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Busca as top histórias do Hacker News"""
        
        # Buscar IDs das top histórias
        response = requests.get(self.top_stories_url, timeout=30)
        if response.status_code != 200:
            raise Exception(f"Erro ao buscar histórias: {response.status_code}")
        
        story_ids = response.json()[:limit]
        
        # Buscar detalhes de cada história
        trends = []
        for story_id in story_ids:
            story = self._fetch_story(story_id)
            if story and story.get('url'):
                trends.append(self._convert_to_trend(story))
        
        return trends
    
    def _fetch_story(self, story_id: int) -> Dict[str, Any]:
        """Busca detalhes de uma história específica"""
        url = f"{self.base_url}/item/{story_id}.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def _convert_to_trend(self, story: Dict[str, Any]) -> Dict[str, Any]:
        """Converte história do HN para formato de tendência"""
        return {
            "source": "hackernews",
            "source_id": str(story.get("id", "")),
            "name": story.get("title", "Sem título"),
            "description": story.get("text", ""),
            "url": story.get("url", f"https://news.ycombinator.com/item?id={story.get('id')}"),
            "category": "tech",
            "metrics": {
                "score": story.get("score", 0),
                "comments": story.get("descendants", 0)
            },
            "detected_at": datetime.now().isoformat(),
            "raw_data": story
        }


class RedditCollector:
    """Coletor de tendências do Reddit (r/MachineLearning)"""
    
    def __init__(self, subreddit: str = "MachineLearning"):
        self.subreddit = subreddit
        self.api_url = f"https://www.reddit.com/r/{subreddit}/hot.json"
    
    def fetch_hot_posts(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Busca posts populares do subreddit"""
        
        headers = {"User-Agent": "TrendArbitrageScout/1.0"}
        response = requests.get(
            self.api_url,
            params={"limit": limit},
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            raise Exception(f"Erro ao buscar posts: {response.status_code}")
        
        data = response.json()
        posts = data.get("data", {}).get("children", [])
        
        trends = []
        for post in posts:
            post_data = post.get("data", {})
            if post_data.get("is_self"):  # Only text posts for better analysis
                trends.append(self._convert_to_trend(post_data))
        
        return trends
    
    def _convert_to_trend(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Converte post do Reddit para formato de tendência"""
        return {
            "source": "reddit",
            "source_id": post.get("id", ""),
            "name": post.get("title", "Sem título"),
            "description": post.get("selftext", "")[:500],
            "url": f"https://reddit.com{post.get('permalink', '')}",
            "category": post.get("subreddit", "MachineLearning"),
            "metrics": {
                "score": post.get("score", 0),
                "comments": post.get("num_comments", 0)
            },
            "detected_at": datetime.now().isoformat(),
            "raw_data": post
        }


class ProductHuntCollector:
    """Coletor de tendências do Product Hunt (via API pública)"""
    
    def __init__(self, api_url: str = "https://api.producthunt.com/v2/posts"):
        self.api_url = api_url
    
    def fetch_daily_posts(self, date: str = None) -> List[Dict[str, Any]]:
        """Busca posts do dia no Product Hunt"""
        # Product Hunt API requer autenticação, então vamos usar scraping simples
        # Por enquanto, retornamos lista vazia - pode ser implementado depois
        return []


def collect_all_trends() -> List[Dict[str, Any]]:
    """Coleta tendências de todas as fontes"""
    
    all_trends = []
    
    # Hacker News
    try:
        hn = HackerNewsCollector()
        hn_trends = hn.fetch_top_stories(30)
        print(f"[Hacker News] Coletadas {len(hn_trends)} tendências")
        all_trends.extend(hn_trends)
    except Exception as e:
        print(f"[Hacker News] Erro: {e}")
    
    # Reddit
    try:
        reddit = RedditCollector()
        reddit_trends = reddit.fetch_hot_posts(30)
        print(f"[Reddit] Coletadas {len(reddit_trends)} tendências")
        all_trends.extend(reddit_trends)
    except Exception as e:
        print(f"[Reddit] Erro: {e}")
    
    return all_trends


if __name__ == "__main__":
    # Teste rápido
    trends = collect_all_trends()
    print(f"\nTotal coletado: {len(trends)} tendências")
    
    # Salvar
    with open("data/raw_trends.json", "w", encoding="utf-8") as f:
        json.dump(trends, f, ensure_ascii=False, indent=2)