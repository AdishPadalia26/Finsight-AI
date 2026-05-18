import json
from graph.nodes import BaseAgent
from tools.financial.calculator import (
    savings_rate, debt_to_income, emergency_fund_months,
    net_worth, total_minimum_debt_payments, total_debt_balance,
    financial_health_score,
)

SYSTEM_PROMPT = """You are the Budget Architect Agent for FinSight AI.

Design a personalized budget system based on the user's financial profile and behavioral patterns.

You have three frameworks available:
- 50/30/20 rule: 50% needs, 30% wants, 20% savings/debt payoff
- Zero-based budgeting: every dollar assigned a purpose, best for impulsive spenders
- Envelope method: fixed category allocations, best for disciplined but inconsistent spenders

Select the framework best suited to the user based on their discipline_score from behavioral data.

Produce:
1. The recommended framework with a clear rationale
2. Specific monthly dollar allocations for each spending category
3. Top 3 actionable spending cuts with EXACT dollar amounts ("Reduce dining from $680 to $400 saves $280/month")
4. A 90-day action plan with 3 concrete numbered steps
5. Use the pre-computed financial health score provided — do NOT recalculate it

STRICT OUTPUT RULES:
- Output ONLY a valid JSON object. No explanation, no markdown, no preamble.
- Start your response with { and end with }
- All recommendations must be mathematically consistent with stated income/expenses
- Do NOT recommend cutting essential expenses below viable minimums (rent, utilities, minimum debt payments)
- Frame recommendations as considerations, not directives — this is NOT licensed advice

Required JSON structure:
{
  "recommended_framework": <string>,
  "framework_rationale": <string>,
  "monthly_allocations": {<category>: <float>},
  "top_cuts": [
    {"category": <string>, "current": <float>, "recommended": <float>, "monthly_savings": <float>, "action": <string>}
  ],
  "health_score": {
    "total": <float>, "grade": <string>,
    "savings_score": <float>, "dti_score": <float>, "emergency_score": <float>
  },
  "action_plan_90_days": [<string>, <string>, <string>],
  "key_finding": <string>
}"""


class BudgetArchitectAgent(BaseAgent):
    """
    Agent 04 — Budget Architect (Tier 2, Parallel)

    Pre-computes all financial ratios before the LLM call — prevents hallucinated numbers.
    Integrates Agent 02 behavioral fingerprint to make recommendations realistic.

    Model: Llama-3.1-70B — complex financial reasoning requires the most capable model.
    """

    MODEL_TYPE = "reasoning"

    def __init__(self):
        super().__init__(name="BudgetArchitectAgent", system_prompt=SYSTEM_PROMPT)

    def run(self, state: dict) -> dict:
        # Pre-compute all math — inject real numbers, LLM only reasons over them
        debts = state.get("debts", [])
        income = state.get("monthly_income", 0)
        expenses = state.get("monthly_expenses", 0)
        savings = state.get("savings", 0)

        min_debt_payments = total_minimum_debt_payments(debts)
        total_debt = total_debt_balance(debts)

        sr = savings_rate(income, expenses)
        dti = debt_to_income(min_debt_payments, income)
        em = emergency_fund_months(savings, expenses)
        nw = net_worth(
            savings,
            state.get("investments", 0),
            state.get("property_value", 0),
            total_debt,
        )
        health = financial_health_score(sr, dti, em)

        behavioral = state.get("behavioral_fingerprint") or {}

        prompt_data = {
            "financial_metrics": {
                "monthly_income": income,
                "monthly_expenses": expenses,
                "monthly_surplus": round(income - expenses, 2),
                "savings_rate_pct": sr,
                "debt_to_income_pct": dti,
                "emergency_fund_months": em,
                "net_worth": nw,
                "total_debt_balance": total_debt,
                "min_monthly_debt_payments": min_debt_payments,
            },
            "pre_computed_health_score": health,
            "behavioral_data": {
                "discipline_score": behavioral.get("discipline_score", "unknown"),
                "spending_categories": behavioral.get("categories", {}),
                "top_anomalies": behavioral.get("anomalies", []),
                "subscription_creep": behavioral.get("subscription_creep", False),
                "key_behavioral_insight": behavioral.get("key_insight", ""),
            },
            "profile": {
                "age": state.get("age"),
                "goals": state.get("goals", []),
                "risk_tolerance": state.get("risk_tolerance"),
            },
        }

        result = self._call_llm_json(json.dumps(prompt_data))
        # Always use pre-computed health score — don't trust LLM math
        result["health_score"] = health

        return {**state, "budget_recommendation": result}
