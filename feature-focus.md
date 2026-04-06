# Feature Focus - Trend Arbitrage Scout

## Projeto
Trend Arbitrage Scout - Automação para identificar tendências dos EUA e replicar no Brasil

## Fonte do Requisito
Squad Estratégia e Engenharia - Documento: PRD_Tech_Delivery.md

## Funcionalidades Priorizadas

### 1. Sistema de Coleta de Dados
- **Prioridade**: ALTA
- **Descrição**: Robô de coleta que busca tendências em Product Hunt, Hacker News, Reddit, App Stores
- **Tecnologia**: Python + Playwright + APIs oficiais

### 2. Motor de Processamento (LM Notebook)
- **Prioridade**: ALTA
- **Descrição**: Pipeline de análise com LLM para calcular scores de Moat e Tropicalização
- **Tecnologia**: Jupyter/LM Notebook + Python

### 3. Sistema de Entrega
- **Prioridade**: MÉDIA
- **Descrição**: Dashboard + Notion + Slack para entrega dos relatórios
- **Tecnologia**: Next.js + n8n + MCPs

### 4. Pipeline de Automação (n8n)
- **Prioridade**: ALTA
- **Descrição**: Workflow automatizado para execução semanal/mensal
- **Tecnologia**: n8n + Cron

## Escopo Técnico

### Colletors a Desenvolver
1. Product Hunt API collector
2. Hacker News API collector  
3. Reddit API collector
4. App Store / Google Play scraper

### Integrações MCP
1. Notion MCP - salvar relatórios
2. Slack MCP - alertas
3. Google Sheets MCP - export

### Database
- PostgreSQL com schema para trends, analysis, reports
- Redis para cache temporário

## Critérios de Sucesso
- [ ] Coleta automática executa sem intervenção
- [ ] Relatório semanal gerado automaticamente
- [ ] Score de tropicalização calculado para cada tendência
- [ ] Dashboard funcional com filtros
- [ ] Integração Notion operacional
- [ ] Integração Slack com alertas operacionais

## Próximos Passos
Ariel: Mapear fontes de dados e seletores necessários
Dante: Implementar estrutura do projeto e collectors
Vera: Revisar código e validar robustez
