# FinSight AI

**Your bank's AI-native wealth intelligence layer — personalized financial guidance at enterprise scale.**

A white-label, multi-agent AI financial intelligence platform built with LangGraph and HuggingFace open-source models. 12 AI agents across 3 tiers deliver personalized financial analysis with real-time market data, adversarial stress-testing, and compliance guardrails.

Built for the Wipro Junior FDE Pre-screening Assignment (May 2026).

---

## Live Demo

> Backend: https://finsight-api.your-cloud.run (Cloud Run — always on)
> Frontend: https://finsight-ai.vercel.app (Vercel — always on)
>
> *(URLs will be updated after deployment)*

---

## Architecture

12 AI agents across 3 tiers:

| Tier | Agents | Purpose |
|---|---|---|
| Tier 1 — Data Intelligence | Profile Builder, Behavioral Pattern, Credit Intelligence | Know the user before advising them |
| Tier 2 — Financial Planning | Budget Architect, Goal Engineering, Investment Strategist, Tax Intelligence, Debt Elimination | Core reasoning and personalized advice |
| Tier 3 — Intelligence & Safety | Life Event Anticipation, Critic (Red Team), Compliance Gate, Memory | Stress-test, safeguard, and remember |

Agents 2–3 run in **parallel** (Tier 1 enrichment). Agents 4–8 run in **parallel** (Tier 2 planning). The Critic Agent runs a **revision loop** (max 3 iterations) before the Compliance Gate delivers the final report.

See `docs/architecture_12_agent.png` for the full diagram.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Framework | LangGraph |
| LLM | HuggingFace Inference API (Mixtral-8x7B, Llama-3.1-70B, Llama-3.3-70B, Mistral-7B) |
| Backend | FastAPI + SSE streaming |
| Frontend | Next.js 14 (TypeScript, Tailwind CSS, recharts) |
| Live Market Data | yfinance (no API key) + FRED API (free) |
| Financial Math | numpy-financial |
| Observability | LangSmith |
| Deployment | Google Cloud Run (backend) + Vercel (frontend) |

---

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- HuggingFace account (free) — accept Llama 3 model licenses at huggingface.co/meta-llama
- FRED API key (free) — fred.stlouisfed.org/docs/api/api_key.html
- LangSmith API key (free) — smith.langchain.com

### 1. Backend

```bash
git clone https://github.com/AdishPadalia26/Finsight-AI
cd Finsight-AI/finsight-ai

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your real keys
```

Required keys in `.env`:
```
HUGGINGFACE_API_KEY=hf_...
FRED_API_KEY=...
LANGSMITH_API_KEY=lsv2_pt_...
```

```bash
uvicorn api.main:app --reload
# Backend running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 2. Frontend

```bash
cd frontend
cp .env.local.example .env.local
# .env.local already has NEXT_PUBLIC_API_URL=http://localhost:8000 for local dev

npm install
npm run dev
# Frontend running at http://localhost:3000
```

---

## Demo Personas

Three pre-loaded financial profiles — click the buttons in the UI to load:

| Persona | Age | Location | Income | Situation |
|---|---|---|---|---|
| Alex | 27 | Austin TX | $5,500/mo | Young professional, student loan + credit card debt, saving for a home |
| Jordan | 42 | Chicago IL | $12,000/mo | Mid-career, mortgage, targeting retirement at 60 |
| Sam | 58 | Seattle WA | $18,000/mo | Pre-retirement, conservative, retiring at 65 |

---

## Security & Guardrails

- **Prompt injection protection** — Profile Builder sanitizes all input before any LLM call
- **Role constraints** — each agent's system prompt strictly limits its domain
- **Defense-in-depth** — Investment Strategist scans its own output for ticker slippage before returning
- **Critic Agent** — adversarially stress-tests the plan across 5 scenarios before delivery
- **Compliance Gate** — CRITICAL violations hard-stop the pipeline; MODERATE violations are rewritten; all outputs receive jurisdiction-appropriate regulatory disclaimers
- **PII handling** — income and asset data never written to logs; only anonymized session IDs stored
- **Audit trail** — every request logged with session ID, timestamp, violations found, and action taken

---

## Running Tests

```bash
pytest tests/
```

---

## Cloud Deployment

**Backend → Google Cloud Run:**
```bash
gcloud run deploy finsight-api \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars HUGGINGFACE_API_KEY=...,FRED_API_KEY=...,LANGSMITH_API_KEY=...
```

**Frontend → Vercel:**
```bash
cd frontend && vercel --prod
# Set NEXT_PUBLIC_API_URL to your Cloud Run URL in Vercel dashboard
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/analyze` | Stream agent events via Server-Sent Events |
| POST | `/analyze/sync` | Blocking analysis — returns full JSON result |
| GET | `/analyze/demo/{persona}` | Load alex / jordan / sam demo persona |
| GET | `/health` | Liveness check |
| GET | `/ready` | Readiness check (verifies API keys present) |
| GET | `/docs` | Interactive API documentation (Swagger UI) |

---

## Disclaimer

This software is for demonstration purposes only. All outputs are AI-generated and do not constitute licensed financial, tax, or legal advice. Past performance does not guarantee future results. Please consult a Certified Financial Planner (CFP) before making financial decisions.
