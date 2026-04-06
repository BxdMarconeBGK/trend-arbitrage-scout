"""
Trend Arbitrage Scout - Processador de Análise
Processa tendências usando Ollama (gratuito, local) ou APIs externas
Autor: Dante (Desenvolvedor)
"""

import json
import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import time


class TrendAnalyzer:
    """Analisador de tendências com suporte a múltiplos provedores"""
    
    def __init__(
        self, 
        provider: str = "ollama",  # "ollama", "openai", "gemini", "fallback"
        model: str = "llama3.2",   # modelo para Ollama
        openai_key: Optional[str] = None,
        gemini_key: Optional[str] = None,
        ollama_url: str = "http://localhost:11434"
    ):
        self.provider = provider
        self.model = model
        self.openai_key = openai_key or os.getenv("OPENAI_API_KEY")
        self.gemini_key = gemini_key or os.getenv("GEMINI_API_KEY")
        self.ollama_url = ollama_url
    
    def analyze_with_llm(self, trend: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa uma tendência usando o provedor configurado"""
        
        prompt = self._build_prompt(trend)
        
        # Tentar provedores em ordem de preferência
        if self.provider == "ollama":
            result = self._analyze_ollama(prompt)
            if result:
                return result
        
        if self.provider == "openai" and self.openai_key:
            result = self._analyze_openai(prompt)
            if result:
                return result
        
        if self.provider == "gemini" and self.gemini_key:
            result = self._analyze_gemini(prompt)
            if result:
                return result
        
        # Fallback para análise baseada em regras
        return self._analyze_fallback(trend)
    
    def _build_prompt(self, trend: Dict[str, Any]) -> str:
        """Constrói o prompt para análise"""
        return f"""Você é um analista de tendências de tecnologia especializado em identificar oportunidades de mercado entre EUA e Brasil.

Analise a seguinte tendência e forneça um JSON com sua avaliação:

Nome: {trend['name']}
Descrição: {trend['description']}
Categoria: {trend['category']}
Fonte: {trend['source']}
Métricas: {trend.get('metrics', {})}

Forneça APENAS um JSON válido (sem texto adicional, sem markdown):
{{
  "moat_score": 0-10,
  "monetization_model": "subscription|freemium|one-time|usage|open-source|hardware|content|community|free",
  "cultural_fit": 0-10,
  "market_demand": 0-10,
  "regulatory_ease": 0-10,
  "tropicalization_score": 0-10,
  "recommended_action": "priority|medium|low",
  "brief_analysis": "uma frase em português explicando o potencial para o Brasil"
}}"""
    
    def _analyze_ollama(self, prompt: str) -> Optional[Dict]:
        """Analisa usando Ollama (local, gratuito)"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "stream": False
                },
                timeout=120
            )
            
            if response.status_code == 200:
                content = response.json()["message"]["content"]
                return self._parse_json_response(content)
        except Exception as e:
            print(f"[Ollama] Erro: {e}")
        return None
    
    def _analyze_openai(self, prompt: str) -> Optional[Dict]:
        """Analisa usando OpenAI (API paga)"""
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                },
                timeout=60
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return self._parse_json_response(content)
        except Exception as e:
            print(f"[OpenAI] Erro: {e}")
        return None
    
    def _analyze_gemini(self, prompt: str) -> Optional[Dict]:
        """Analisa usando Google Gemini (API gratuita disponível)"""
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.gemini_key}",
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 500
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                content = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                return self._parse_json_response(content)
        except Exception as e:
            print(f"[Gemini] Erro: {e}")
        return None
    
    def _parse_json_response(self, content: str) -> Optional[Dict]:
        """Extrai JSON da resposta do LLM"""
        content = content.strip()
        
        # Remove markdown se presente
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        # Remove texto antes ou depois do JSON
        if "{" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            content = content[start:end]
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print("[Parser] Erro ao parsear JSON")
            return None
    
    def _analyze_fallback(self, trend: Dict[str, Any]) -> Dict[str, Any]:
        """Análise baseada em regras quando LLM não está disponível"""
        
        # heuristics simples baseadas em métricas
        metrics = trend.get("metrics", {})
        score = metrics.get("score", 0)
        comments = metrics.get("comments", 0)
        
        # Calcular popularidade normalizada (0-10)
        popularity = min(10, (score / 100) + (comments / 50))
        
        # Ajustar baseado na fonte
        source = trend.get("source", "")
        if source == "hackernews":
            popularity *= 1.2  # HN é mais técnico/empreendedor
        elif source == "reddit":
            popularity *= 0.9  # Reddit tem mais ruído
        
        popularity = min(10, popularity)
        
        return {
            "moat_score": round(5 + (popularity * 0.3)),
            "monetization_model": "unknown",
            "cultural_fit": round(5 + (popularity * 0.4)),
            "market_demand": round(5 + (popularity * 0.5)),
            "regulatory_ease": 7,
            "tropicalization_score": round(5 + (popularity * 0.4), 1),
            "recommended_action": "priority" if popularity > 7 else "medium" if popularity > 4 else "low",
            "brief_analysis": f"Análise automática baseada em métricas: {score} pontos, {comments} comentários."
        }
    
    def analyze_batch(self, trends: List[Dict[str, Any]], save_progress: bool = True) -> List[Dict[str, Any]]:
        """Analisa múltiplas tendências"""
        results = []
        
        for i, trend in enumerate(trends):
            print(f"[Analisando {i+1}/{len(trends)}] {trend['name'][:50]}...")
            
            analysis = self.analyze_with_llm(trend)
            
            result = {
                **trend,
                **analysis,
                "analyzed_at": datetime.now().isoformat()
            }
            
            results.append(result)
            
            # Salvar progresso a cada 5 tendências
            if save_progress and (i + 1) % 5 == 0:
                self._save_progress(results, f"data/progress_{i+1}.json")
            
            # Peque pausa para não sobrecarregar API
            time.sleep(0.5)
        
        return results
    
    def _save_progress(self, results: List[Dict], filename: str):
        """Salva progresso intermediário"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)


def calculate_tropicalization(analysis: Dict) -> float:
    """Calcula score de tropicalização"""
    cultural = analysis.get("cultural_fit", 5)
    market = analysis.get("market_demand", 5)
    regulatory = analysis.get("regulatory_ease", 5)
    
    score = (cultural * 0.4) + (market * 0.3) + (regulatory * 0.3)
    return round(score, 1)


def sort_by_priority(results: List[Dict]) -> List[Dict]:
    """Ordena resultados por prioridade"""
    priority_order = {"priority": 0, "medium": 1, "low": 2}
    
    return sorted(
        results,
        key=lambda x: (
            priority_order.get(x.get("recommended_action"), 1),
            -x.get("tropicalization_score", 0)
        )
    )


if __name__ == "__main__":
    import sys
    
    # Permite especificar provedor via argumento
    provider = sys.argv[1] if len(sys.argv) > 1 else "fallback"
    
    print(f"[TrendAnalyzer] Usando provedor: {provider}")
    
    # Carregar tendências coletadas
    with open("data/raw_trends.json", "r", encoding="utf-8") as f:
        trends = json.load(f)
    
    print(f"[TrendAnalyzer] Carregadas {len(trends)} tendências")
    
    # Analisar
    analyzer = TrendAnalyzer(provider=provider)
    analyzed = analyzer.analyze_batch(trends)
    
    # Ordenar por prioridade
    sorted_results = sort_by_priority(analyzed)
    
    # Salvar resultado
    with open("data/analyzed_trends.json", "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Salvo] {len(sorted_results)} tendências analisadas em data/analyzed_trends.json")