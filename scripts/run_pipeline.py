"""
Trend Arbitrage Scout - Script Principal
Executa o pipeline completo de coleta e análise
Autor: Dante
"""

import asyncio
import json
import os
import sys
from datetime import datetime

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from collectors import ProductHuntCollector, HackerNewsCollector, RedditCollector
from processors.analyzer import TrendAnalyzer, sort_by_priority


async def collect_trends():
    """Coleta tendências de todas as fontes"""
    
    print("=" * 50)
    print("TREND ARBITRAGE SCOUT - COLETA")
    print("=" * 50)
    
    collectors = [
        ProductHuntCollector(),
        HackerNewsCollector(),
        RedditCollector(),
    ]
    
    all_trends = []
    
    for collector in collectors:
        print(f"\n[Coletando] {collector.source_name}...")
        try:
            trends = await collector.run()
            all_trends.extend(trends)
            print(f"  OK {len(trends)} tendencias coletadas")
        except Exception as e:
            print(f"  ERRO: {e}")
    
    print(f"\n[Total] {len(all_trends)} tendências coletadas")
    
    # Salvar dados brutos
    os.makedirs("data", exist_ok=True)
    with open("data/raw_trends.json", "w", encoding="utf-8") as f:
        json.dump(all_trends, f, ensure_ascii=False, indent=2)
    
    return all_trends


def analyze_trends(trends):
    """Analisa tendências usando LM Studio"""
    
    print("\n" + "=" * 50)
    print("TREND ARBITRAGE SCOUT - ANÁLISE")
    print("=" * 50)
    
    analyzer = TrendAnalyzer(lm_url="http://localhost:1234")
    
    print(f"\n[Processando] {len(trends)} tendências com LM Studio...")
    print("(Aguarde, isso pode levar alguns minutos)\n")
    
    analyzed = analyzer.analyze_batch(trends)
    
    # Ordenar por prioridade
    sorted_results = sort_by_priority(analyzed)
    
    # Salvar resultado
    with open("data/analyzed_trends.json", "w", encoding="utf-8") as f:
        json.dump(sorted_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[Salvo] {len(sorted_results)} tendências analisadas")
    
    return sorted_results


def generate_report(trends):
    """Gera relatório em formato simple"""
    
    print("\n" + "=" * 50)
    print("TREND ARBITRAGE SCOUT - RELATÓRIO")
    print("=" * 50)
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_trends": len(trends),
        "top_opportunities": [],
        "by_source": {},
        "by_action": {"priority": 0, "medium": 0, "low": 0}
    }
    
    # Top 10 oportunidades
    for trend in trends[:10]:
        report["top_opportunities"].append({
            "name": trend["name"],
            "description": trend["description"][:100] + "...",
            "source": trend["source"],
            "tropicalization_score": trend.get("tropicalization_score", 0),
            "moat_score": trend.get("moat_score", 0),
            "action": trend.get("recommended_action", "medium")
        })
    
    # Estatísticas por fonte
    for trend in trends:
        source = trend["source"]
        if source not in report["by_source"]:
            report["by_source"][source] = 0
        report["by_source"][source] += 1
        
        action = trend.get("recommended_action", "medium")
        report["by_action"][action] = report["by_action"].get(action, 0) + 1
    
    # Salvar relatório
    with open("data/report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # Gerar Markdown
    md_content = f"""# 📊 Trend Arbitrage Scout - Relatório Semanal

**Gerado em**: {datetime.now().strftime('%d/%m/%Y %H:%M')}
**Total de tendências**: {len(trends)}

## 🔥 Top 10 Oportunidades

| # | Nome | Fonte | Score 🌴 | Moat | Ação |
|---|------|-------|----------|------|------|
"""
    
    for i, trend in enumerate(trends[:10], 1):
        name = trend["name"][:30]
        source = trend["source"]
        tropical = trend.get("tropicalization_score", 0)
        moat = trend.get("moat_score", 0)
        action = trend.get("recommended_action", "medium")
        
        emoji = "🔴" if action == "priority" else "🟡" if action == "medium" else "🟢"
        
        md_content += f"| {i} | {name} | {source} | {tropical} | {moat} | {emoji} |\n"
    
    md_content += f"""
## 📈 Estatísticas

**Por Fonte:**
"""
    
    for source, count in report["by_source"].items():
        md_content += f"- {source}: {count}\n"
    
    md_content += f"""
**Por Prioridade:**
- 🔴 Priority: {report["by_action"].get('priority', 0)}
- 🟡 Medium: {report["by_action"].get("medium", 0)}
- 🟢 Low: {report['by_action'].get('low', 0)}

---
*Gerado automaticamente pelo Trend Arbitrage Scout*
"""
    
    with open("data/report.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print("[Salvo] Relatório gerado em data/report.md")
    
    return report


async def main():
    """Pipeline principal"""
    
    # 1. Coletar
    trends = await collect_trends()
    
    if not trends:
        print("\nERRO Nenhuma tendencia coletada. Encerrando.")
        return
    
    # 2. Analisar
    analyzed = analyze_trends(trends)
    
    # 3. Gerar relatório
    report = generate_report(analyzed)
    
    print("\n" + "=" * 50)
    print("✅ PIPELINE CONCLUÍDO")
    print("=" * 50)
    print("\nArquivos gerados:")
    print("  - data/raw_trends.json")
    print("  - data/analyzed_trends.json")
    print("  - data/report.json")
    print("  - data/report.md")


if __name__ == "__main__":
    asyncio.run(main())
