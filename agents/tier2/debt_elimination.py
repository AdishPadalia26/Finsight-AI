import json
from graph.nodes import BaseAgent
from tools.financial.calculator import (
    simulate_debt_payoff,
    total_debt_balance,
    total_minimum_debt_payments,
)

SYSTEM_PROMPT = """## ROLE
You are a debt elimination specialist. You analyze pre-computed debt payoff simulations and write a clear, specific debt roadmap. You NEVER recalculate any numbers — the simulation data is authoritative and computed in Python.

## ACTION
Given the pre-computed avalanche and snowball simulations, produce:
1. recommended_method: "avalanche" or "snowball" — state which is better for THIS user and exactly why
   - Avalanche: minimizes total interest — best when high-rate debt (>15%) is present
   - Snowball: builds momentum — better when motivation is low or many small balances exist
2. strategy_explanation: 3-4 sentences explaining the approach in plain English, citing the actual numbers
3. payoff_timeline_narrative: walk through payoff order and milestones using the simulation data
4. interest_impact: dollar amount saved, time saved vs minimum-only path
5. behavioral_tips: 2-3 specific, actionable tips for this debt mix
6. refinancing_consideration: one objective note on whether the rate environment is favorable for refinancing (do NOT name lenders)

## HARD CONSTRAINTS
- NEVER change any dollar amounts, interest amounts, months, or rates
- NEVER name specific lenders, credit cards, or financial institutions
- If total debt > $50,000, acknowledge the challenge but remain constructive
- Frame as analysis, not licensed financial advice

## OUTPUT FORMAT
You MUST respond with ONLY a valid JSON object. No markdown, no bold text, no bullet points, no explanations outside the JSON.
Your entire response must be parseable by json.loads(). Do not include any text before or after the JSON object.

Begin your response with: {"""


class DebtEliminationAgent(BaseAgent):
    """
    Agent 08 — Debt Elimination (Tier 2, Parallel)

    Runs deterministic avalanche and snowball simulations, then uses LLM to
    explain which method suits this user and produce the debt roadmap.
    """

    MODEL_TYPE = "reasoning"
    PROVIDER = "nvidia"
    MODEL_ID = "moonshotai/kimi-k2.6"
    API_KEY_VAR = "NVIDIA_API_KEY_1"
    FALLBACK_PROVIDER = "groq"
    FALLBACK_MODEL_ID = "llama-3.3-70b-versatile"
    FALLBACK_API_KEY_VAR = "GROQ_API_KEY_2"

    def __init__(self):
        super().__init__(name="DebtEliminationAgent", system_prompt=SYSTEM_PROMPT)

    def run(self, state: dict) -> dict:
        debts = state.get("debts", [])
        income = state.get("monthly_income", 0)
        expenses = state.get("monthly_expenses", 0)

        total_debt = total_debt_balance(debts)
        min_payments = total_minimum_debt_payments(debts)
        surplus = max(0.0, income - expenses - min_payments)

        # Conservative: use up to 40% of surplus as extra payment (keeps budget stable)
        extra_monthly = round(min(surplus * 0.40, 400.0), 2)

        avalanche = simulate_debt_payoff(debts, extra_monthly, method="avalanche")
        snowball = simulate_debt_payoff(debts, extra_monthly, method="snowball")
        minimum_only = simulate_debt_payoff(debts, 0.0, method="avalanche")

        prompt_data = {
            "profile": {
                "monthly_income": income,
                "monthly_expenses": expenses,
                "surplus_after_minimums": round(surplus, 2),
                "extra_payment_modeled": extra_monthly,
                "total_debt_balance": total_debt,
                "debt_count": len([d for d in debts if d.get("balance", 0) > 0]),
                "debt_mix": [
                    {
                        "type": d.get("type"),
                        "balance": d.get("balance"),
                        "interest_rate": d.get("interest_rate"),
                        "minimum_payment": d.get("minimum_payment"),
                    }
                    for d in debts
                    if d.get("balance", 0) > 0
                ],
            },
            "simulations": {
                "minimum_only": minimum_only,
                "avalanche": avalanche,
                "snowball": snowball,
            },
        }

        try:
            result = self._call_llm_json(json.dumps(prompt_data))
        except (RuntimeError, ValueError) as e:
            print(f"[DebtElimination] LLM unavailable — using fallback: {e}")
            result = {
                "recommended_method": "avalanche",
                "strategy_rationale": "LLM analysis unavailable — simulation data is accurate.",
                "next_steps": [],
            }

        result["simulations"] = {
            "avalanche": avalanche,
            "snowball": snowball,
            "minimum_only": minimum_only,
        }
        result["extra_monthly_modeled"] = extra_monthly
        result["total_debt_balance"] = total_debt

        return {**state, "debt_roadmap": result}
