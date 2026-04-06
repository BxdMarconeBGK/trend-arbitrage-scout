# 🌴 Trend Arbitrage Scout

Dashboard para identificar tendências dos EUA e replicar no Brasil.

## Arquitetura

| Componente | Tecnologia |
|------------|------------|
| Coleta | Python + APIs gratuitas |
| Processamento | LM Studio (gratuito) |
| Database | JSON local / Google Sheets |
| Dashboard | Next.js → Netlify (grátis) |
| Scheduler | GitHub Actions (grátis) |

## Estrutura

```
trend-arbitrage-scout/
├── collectors/         # Coleta de dados (Product Hunt, HN, Reddit)
├── processors/         # Processamento com LM Studio
├── scripts/           # Pipeline principal
├── data/              # Dados gerados
├── dashboard/         # Site Next.js
├── .github/workflows/ # Automação semanal
└── requirements.txt   # Dependências Python
```

## Como Executar

### 1. Setup do Ambiente

```bash
# Clone o projeto
git clone https://github.com/seu-usuario/trend-arbitrage-scout.git
cd trend-arbitrage-scout

# Instale dependências Python
pip install -r requirements.txt

# Instale Playwright
playwright install --with-deps
```

### 2. Execute a Coleta

```bash
python scripts/run_pipeline.py
```

### 3. Inicie o Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Acesse: http://localhost:3000

## Deploy no Netlify

1. Fork este repositório
2. Vá para Netlify → "New site from Git"
3. Selecione seu fork
4. Build command: `npm run build`
5. Publish directory: `dashboard/out`
6. Deploy!

## Automação Semanal

O GitHub Actions está configurado para executar toda segunda-feira 8:00 UTC.

Você pode acionar manualmente em: Actions → "Weekly Run" → "Run workflow"

## Integração com Google Sheets (Opcional)

Para salvar os dados no Google Sheets:

1. Crie um projeto no Google Cloud
2. Ative a Google Sheets API
3. Crie credenciais (Service Account)
4. Compartilhe sua planilha com o email da service account
5. Adicione as credenciais ao seu projeto

## Screenshots

O dashboard inclui:
- 📊 Cards de estatísticas
- 📈 Gráficos de tropicalização
- 🔥 Lista de oportunidades priorizadas
- 🏷️ Filtros por fonte

## Tecnologias Gratuitas Usadas

- **Product Hunt API** - Grátis
- **Hacker News API** - Grátis
- **Reddit API** - Grátis
- **LM Studio** - Grátis (local)
- **GitHub Actions** - Grátis
- **Netlify** - Grátis (até 100GB)
- **Next.js** - Grátis

## Licença

MIT
