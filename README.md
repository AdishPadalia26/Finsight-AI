# FinSight AI

**Your bank's AI-native wealth intelligence layer — personalized financial guidance at enterprise scale.**

A white-label, multi-agent AI financial intelligence platform built with LangGraph and Claude Sonnet. Deployed by banks and wealth management firms to give every retail customer access to personalized financial analysis — scaling personalized advice from 500 clients per advisor to 50,000.

Built for the Wipro Junior FDE Pre-screening Assignment (May 2026).

---

## Live Demo

> URL will be added after deployment

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
| LLM | Claude Sonnet (`claude-sonnet-4-20250514`) |
| Backend | FastAPI |
| Frontend | Streamlit |
| Live Market Data | Alpha Vantage API + FRED API |
| Financial Math | numpy-financial |
| Observability | LangSmith |
| Deployment | Render |

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/your-username/finsight-ai
cd finsight-ai
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Fill in your API keys in .env
```

Required keys:
- `ANTHROPIC_API_KEY` — get at console.anthropic.com
- `ALPHA_VANTAGE_API_KEY` — free at alphavantage.co
- `FRED_API_KEY` — free at fred.stlouisfed.org
- `LANGSMITH_API_KEY` — free at smith.langchain.com

### 3. Run the backend

```bash
uvicorn api.main:app --reload
```

### 4. Run the frontend

```bash
streamlit run frontend/app.py
```

---

## Demo Personas

Three pre-loaded financial profiles for live demo:

| Persona | Age | Income | Situation |
|---|---|---|---|
| Alex | 27 | $5,500/mo | Young professional, student loan + credit card debt, saving for a home |
| Jordan | 42 | $12,000/mo | Mid-career, mortgage, targeting retirement at 60 |
| Sam | 58 | $18,000/mo | Pre-retirement, conservative, retiring at 65 |

---

## Security & Guardrails

- **Prompt injection protection** — Profile Builder sanitizes all input before any LLM call
- **Role constraints** — each agent's system prompt strictly limits its domain
- **Defense-in-depth** — Investment Strategist scans its own output for ticker slippage
- **Critic Agent** — adversarially stress-tests the plan across 5 scenarios before delivery
- **Compliance Gate** — final guardrail: CRITICAL violations hard-stop the pipeline; MODERATE violations are rewritten; all outputs receive regulatory disclaimers
- **PII handling** — income and asset data never written to logs; only anonymized session IDs stored
- **Audit trail** — every output logged with session ID, timestamp, violations found, and action taken

---

## Running Tests

```bash
pytest tests/
```

---

## Disclaimer

This software is for demonstration purposes only. All outputs are AI-generated and do not constitute licensed financial, tax, or legal advice. Past performance does not guarantee future results. Please consult a Certified Financial Planner (CFP) before making financial decisions.
