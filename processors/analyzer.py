"""
Trend Arbitrage Scout - Processador de Análise
Processa tendências usando LM Studio (gratuito)
Autor: Dante (Desenvolvedor)
"""

import json
import os
import requests
from typing import List, Dict, Any
from datetime import datetime


class TrendAnalyzer:
    """Analisador de tendências usando LM Studio (gratuito)"""
    
    def __init__(self, lm_url: str = "http://localhost:1234"):
        self.lm_url = lm_url
        self.model = "local-model"
    
    def analyze_with_lm(self, trend: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa uma tendência usando LM Studio"""
        
        prompt = f"""Você é um analista de tendências de tecnologia.
Analise a seguinte ferramenta/site e forneça um JSON com sua avaliação:

Nome: {trend['name']}
Descrição: {trend['description']}
Categoria: {trend['category']}
Fonte: {trend['source']}

Forneça APENAS um JSON válido (sem texto adicional):
{{
  "moat_score": 0-10,
  "monetization_model": "subscription|freemium|one-time|usage|unknown",
  "cultural_fit": 0-10,
  "market_demand": 0-10,
  "regulatory_ease": 0-10,
  "tropicalization_score": 0-10,
  "recommended_action": "priority|medium|low",
  "brief_analysis": "uma frase explicando"
}}"""
        
        # Tentar LM Studio primeiro
        try:
            response = requests.post(
                f"{self.lm_url}/v1/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                },
                timeout=60
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                # Extrair JSON da resposta
                content = content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]
                
                return json.loads(content)
        except Exception as e:
            print(f"[LM Studio] Erro: {e}")
        
        # Fallback: retornar análise padrão
        return {
            "moat_score": 5,
            "monetization_model": "unknown",
            "cultural_fit": 5,
            "market_demand": 5,
            "regulatory_ease": 5,
            "tropicalization_score": 5,
            "recommended_action": "medium",
            "brief_analysis": "Análise automática não disponível"
        }
    
    def analyze_batch(self, trends: List[Dict[str, Any]], save_progress: bool = True) -> List[Dict[str, Any]]:
        """Analisa múltiplas tendências"""
        results = []
        
        for i, trend in enumerate(trends):
            print(f"[Analisando {i+1}/{len(trends)}] {trend['name']}")
            
            analysis = self.analyze_with_lm(trend)
            
            result = {
                **trend,
                **analysis,
                "analyzed_at": datetime.now().isoformat()
            }
            
            results.append(result)
            
            # Salvar progresso a cada 5 tendências
            if save_progress and (i + 1) % 5 == 0:
                self._save_progress(results, f"data/progress_{i+1}.json")
        
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
    # Carregar tendências coletadas
    with open("data/raw_trends.json", "r", encoding="utf-8") as f:
        trends = json.load(f)
    
    # Analisar
    analyzer = TrendAnalyzer()
    analyzed = analyzer.analyze_batch(trends)
    
    # Ordenar por prioridade
    sorted_results = sort_by_priority(analyzed)
    
    # Salvar resultado
    with open("data/analyzed_trends.json", "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Salvo] {len(sorted_results)} tendências analisadas em data/analyzed_trends.json")
