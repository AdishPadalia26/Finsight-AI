import json
from graph.nodes import BaseAgent
from tools.financial.calculator import (
    savings_rate, debt_to_income, emergency_fund_months,
    net_worth, total_minimum_debt_payments, total_debt_balance,
    financial_health_score,
)

SYSTEM_PROMPT = """## ROLE
You are a certified financial planner (CFP) specializing in personal budget optimization. You analyze pre-computed financial ratios and write specific, actionable budget recommendations. You do NOT recalculate numbers — they are provided to you. Be direct and specific — never hedge with "consider" or "you might want to."

## ACTION
Given the pre-computed financial data provided, produce a complete budget health report with:
1. A recommended_framework: which budget system fits this person (50/30/20, zero-based, or envelope) with rationale
   - 50/30/20: best for "disciplined" or "average" spenders with stable income
   - Zero-based: best for "impulsive" spenders — every dollar gets a job
   - Envelope: best for people who overspend specific categories repeatedly
2. monthly_allocations: specific dollar amounts for every spending category
3. top_cuts: exactly 3 specific, dollar-quantified actions — format: "Reduce [category] from $X to $Y/month, saving $Z"
4. action_plan_90_days: 3 numbered, concrete steps the user can execute this week/month/quarter
5. key_finding: one sentence summarizing the single most important finding
6. Use the pre_computed_health_score exactly as provided — do NOT recalculate it

## CONTEXT
You receive pre-computed metrics (savings rate, DTI, emergency fund months, net worth) and behavioral data (spending categories, anomalies, discipline score). All numbers are accurate — trust them.

## HARD CONSTRAINTS — Never violate these
- Do NOT recalculate or modify any numbers given to you
- All dollar amounts in recommendations must be derivable from the provided data
- Never recommend cutting essential expenses below minimums (rent, utilities, minimum debt payments)
- Never recommend specific financial products, banks, or credit cards by name
- Every top_cut must include an exact monthly_savings dollar amount
- This is NOT licensed financial advice — frame findings as analysis, not directives

## Think step by step before producing output:
1. Check discipline_score to select the right framework
2. Identify the top 3 overspending categories vs. 50/30/20 benchmarks
3. Calculate specific cut amounts that are mathematically possible given income/expenses
4. Verify: do monthly_allocations sum to approximately monthly_income?
5. Write action_plan steps that are actionable within 90 days
6. Return the JSON

Respond only in valid JSON. Begin your response with: {"""


class BudgetArchitectAgent(BaseAgent):
    """
    Agent 04 — Budget Architect (Tier 2, Parallel)

    Pre-computes all financial ratios before the LLM call — prevents hallucinated numbers.
    Integrates Agent 02 behavioral fingerprint to make recommendations realistic.

    Model: Llama-3.1-70B — complex financial reasoning requires the most capable model.
    """

    MODEL_TYPE = "reasoning"
    PROVIDER = "openrouter"
    MODEL_ID = "google/gemma-4-31b-it:free"
    API_KEY_VAR = "OPENROUTER_API_KEY_1"
    FALLBACK_PROVIDER = "groq"
    FALLBACK_MODEL_ID = "llama-3.3-70b-versatile"
    FALLBACK_API_KEY_VAR = "GROQ_API_KEY_1"

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

        try:
            result = self._call_llm_json(json.dumps(prompt_data))
        except (RuntimeError, ValueError) as e:
            print(f"[BudgetArchitect] LLM unavailable — using fallback: {e}")
            result = {
                "recommended_framework": "50/30/20",
                "key_finding": "LLM analysis unavailable — pre-computed metrics are accurate.",
                "top_cuts": [],
                "monthly_allocations": {},
                "action_plan_90_days": [],
            }

        # Normalize string fields that the LLM may return as objects
        if not isinstance(result.get("recommended_framework"), str):
            result["recommended_framework"] = json.dumps(result.get("recommended_framework")) if result.get("recommended_framework") else "50/30/20"
        if not isinstance(result.get("key_finding"), str):
            result["key_finding"] = json.dumps(result.get("key_finding")) if result.get("key_finding") else ""
        # Always inject pre-computed values — override any LLM-invented numbers
        result["health_score"] = health
        result["savings_rate"] = sr
        result["debt_to_income"] = dti
        result["emergency_fund_months"] = em
        result["monthly_surplus"] = round(income - expenses, 2)
        result["net_worth"] = nw
        result["total_debt_balance"] = total_debt

        return {**state, "budget_recommendation": result}
