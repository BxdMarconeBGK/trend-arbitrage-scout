# 📋 Plano de Implementação - Trend Arbitrage Scout

## Passo a Passo: GitHub + Netlify

---

## 1️⃣ CRIAR REPOSITÓRIO NO GITHUB

### 1.1 - Acesse GitHub
```
URL: https://github.com
```

### 1.2 - Criar novo repositório
1. Clique no botão **"+"** (topo direito) → **"New repository"**
2. **Repository name**: `trend-arbitrage-scout`
3. **Description**: `Dashboard de tendências EUA → Brasil`
4. **Public**: ✅ (marcado)
5. **✓ Add a README file**: Não marque (já temos)
6. **✓ Add .gitignore**: None
7. **Choose a license**: MIT
8. Clique em **"Create repository"**

### 1.3 - Copiar arquivos do projeto
Após criar, o GitHub vai mostrar instruções. Siga estes comandos no seu terminal:

```bash
# No seu computador, na pasta do projeto:
cd "C:\Users\Marcone\Desktop\teste opensquad\projects\trend-arbitrage-scout"

git init
git add .
git commit -m "Initial commit - Trend Arbitrage Scout"

git remote add origin https://github.com/SEU_USUARIO/trend-arbitrage-scout.git
git push -u origin main
```

> ⚠️ **Substitua SEU_USUARIO pelo seu username do GitHub**

---

## 2️⃣ CONFIGURAR GITHUB ACTIONS (Automação Semanal)

### 2.1 - Acessar Actions
1. No seu repositório GitHub → clique na aba **"Actions"**

### 2.2 - Habilitar Actions
1. Clique em **"I understand my workflows, go ahead and enable them"**

### 2.3 - O workflow já está configurado!
O arquivo `.github/workflows/weekly.yml` já está no projeto.
- Ele executa toda **segunda-feira às 8:00 UTC**
- Você pode executar manualmente: Actions → "Weekly Run" → "Run workflow"

### 2.4 (Opcional) - Adicionar secrets
Se quiser usar LM Studio remoto:

1. No repositório → **Settings** → **Secrets and variables** → **Actions**
2. Clique em **"New repository secret"**
3. Name: `LM_STUDIO_URL`
4. Value: `http://seu-ip:1234` (IP da máquina onde roda LM Studio)
5. Clique em **"Add secret"**

---

## 3️⃣ DEPLOY NO NETLIFY (Dashboard Grátis)

### 3.1 - Acesse Netlify
```
URL: https://app.netlify.com
```

### 3.2 - Criar nova aplicação
1. Clique em **"Add new site"** → **"Import an existing project"**

### 3.3 - Conectar ao GitHub
1. Clique em **"GitHub"** (autorize se necessário)
2. Selecione o repositório `trend-arbitrage-scout`

### 3.4 - Configurar build
Preencha os campos:

| Campo | Valor |
|-------|-------|
| **Base directory** | `dashboard` |
| **Build command** | `npm run build` |
| **Publish directory** | `dashboard/out` |

### 3.5 - Variables (opcional)
Clique em **"Show advanced"** → **"New variable`**:

| Name | Value |
|------|-------|
| `NODE_VERSION` | `18` |

### 3.6 - Deploy
1. Clique em **"Deploy site"**
2. Aguarde ~2 minutos
3. ✅ Pronto! Você terá uma URL como `https://trend-arbitrage-scout.netlify.app`

### 3.7 - Configurar domínio customizado (opcional)
- Settings → Domain management
- Você pode conectar um domínio próprio

---

## 4️⃣ CONFIGURAR LM STUDIO (Processamento de IA)

### 4.1 - Baixar LM Studio
```
URL: https://lmstudio.ai
```

### 4.2 - Instalar e abrir
1. Instale o app
2. Abra o app
3. Na barra lateral, busque e baixe um modelo (ex: "Llama 3" ou "Mistral")
4. Clique em **"Start server"** (ícone de play)
5. O server vai rodar em `http://localhost:1234`

### 4.3 - Testar
Abra o terminal e teste:
```bash
curl http://localhost:1234/v1/models
```

Se responder, está funcionando!

---

## 5️⃣ EXECUTAR PIPELINE MANUAL

### 5.1 - No seu computador
```bash
cd "C:\Users\Marcone\Desktop\teste opensquad\projects\trend-arbitrage-scout"

# Ative o ambiente virtual (se tiver)
# Ative o LM Studio e inicie o server

# Execute o pipeline
python scripts/run_pipeline.py
```

### 5.2 - Ver resultados
Os arquivos serão salvos em `data/`:
- `raw_trends.json` - Dados coletados
- `analyzed_trends.json` - Dados processados
- `report.md` - Relatório em markdown
- `report.json` - Relatório em JSON

### 5.3 - Atualizar GitHub
```bash
git add .
git commit -m "Update trend report"
git push
```

O Netlify vai detectar a mudança e atualizar o dashboard automaticamente!

---

## 6️⃣ FLUXO COMPLETO DE FUNCIONAMENTO

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXO AUTOMÁTICO                             │
└─────────────────────────────────────────────────────────────────┘

1. GitHub Actions (segunda 8:00 UTC)
       ↓
2. Executa script Python (collect + analyze)
       ↓
3. LM Studio processa dados (se disponível)
       ↓
4. Salva dados em data/ (JSON)
       ↓
5. Você faz git push dos dados
       ↓
6. Netlify detecta mudança
       ↓
7. Dashboard atualiza com novos dados
```

---

## 7️⃣ RESUMO - O QUE PRECISA FAZER

| # | Passo | Onde | Tempo |
|---|-------|------|-------|
| 1 | Criar repo GitHub | github.com | 2 min |
| 2 | Push código | Terminal | 1 min |
| 3 | Deploy Netlify | netlify.com | 3 min |
| 4 | Baixar LM Studio | lmstudio.ai | 5 min |
| 5 | Testar pipeline | Terminal | 5 min |

**Tempo total: ~15 minutos**

---

## 8️⃣ DÚVIDAS COMUNS

**P: Preciso pagar algo?**
R: Não! Tudo é gratuito:
- GitHub:grátis
- Netlify:grátis (até 100GB)
- LM Studio:grátis
- APIs:gratuitas

**P: O dashboard vai atualizar automaticamente?**
R: Não automaticamente. Você precisa fazer o push dos dados ou configurar a integração GitHub + Google Sheets.

**P: Posso mudar o nome do projeto?**
R: Sim, mas precisa atualizar em vários lugares. Recomendo manter o nome.

---

## 📞 Precisa de ajuda?

Se tiver dúvidas em algum passo, me peça que explico com mais detalhes!
