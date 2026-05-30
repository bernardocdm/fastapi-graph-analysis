# FastAPI Graph Analysis

Análise de colaboração em FastAPI usando Grafos Direcionados e Ponderados.

## 🚀 Quick Start

### 1. Clonar repositório
```bash
git clone https://github.com/bernardocdm/fastapi-graph-analysis.git
cd fastapi-graph-analysis
```

### 2. Criar e ativar ambiente virtual
```bash
python -m venv venv

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

## 📁 Estrutura
src/
├── mining/          # Coleta de dados do GitHub (Nome 1)
├── graph/           # API de grafos (Nome 2)
├── analysis/        # Análise e métricas (Nome 3)
└── export/          # Export GEXF/JSON (Nome 3)
tests/               # Testes unitários
data/                # raw/ → processed/ → outputs/
docs/                # Documentação
relatorio/           # Relatório LaTeX

## 📊 Objetivo

Minerador dados do FastAPI → Construir grafos → Analisar centralidades → Visualizar no Gephi

## 📚 Documentação

Ver pasta `/docs` para planejamento completo:
- `LEIA_PRIMEIRO.txt` - Comece aqui
- `RESUMO_EXECUTIVO.md` - Decisões confirmadas
- `CHECKLIST_SEMANAL.md` - Timeline dia a dia

## 🧪 Testes

```bash
pytest tests/ -v --cov=src
```

## 🔗 Links

- FastAPI: https://github.com/encode/fastapi
- Gephi: https://gephi.org/
- NetworkX: https://networkx.org/

---

**Status:** Em desenvolvimento  