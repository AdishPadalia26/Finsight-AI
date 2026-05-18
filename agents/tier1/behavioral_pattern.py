import json
import random
from graph.nodes import BaseAgent

SYSTEM_PROMPT = """You are the Behavioral Pattern Agent for FinSight AI.

Analyze spending patterns and identify behavioral insights to personalize the financial plan.

Given a financial profile and 6 months of transaction history, you will:
1. Categorize spending into buckets: housing, food, transport, entertainment, subscriptions, health, shopping, utilities, other
2. Identify the top 3 spending anomalies (categories unusually high relative to income)
3. Detect lifestyle inflation signals (expenses growing relative to income)
4. Flag subscription creep (many small recurring charges totaling > 5% of income)
5. Assess overall spending discipline: "disciplined", "average", or "impulsive"
6. Write ONE key insight sentence

Be specific with dollar amounts. Be direct but not judgmental.

STRICT OUTPUT RULES:
- Output ONLY a valid JSON object. No explanation, no markdown, no preamble.
- Start your response with { and end with }

Required JSON structure:
{
  "categories": {
    "housing": <float>, "food": <float>, "transport": <float>,
    "entertainment": <float>, "subscriptions": <float>, "health": <float>,
    "shopping": <float>, "utilities": <float>, "other": <float>
  },
  "anomalies": [
    {"category": <string>, "monthly_amount": <float>, "benchmark": <float>, "overspend": <float>}
  ],
  "lifestyle_inflation": <boolean>,
  "subscription_creep": <boolean>,
  "total_subscriptions_monthly": <float>,
  "discipline_score": <string>,
  "key_insight": <string>
}"""


class BehavioralPatternAgent(BaseAgent):
    """
    Agent 02 — Behavioral Pattern (Tier 1, Parallel)

    Analyzes spending behavior from transaction history.
    For the demo, generates realistic mock transactions from the profile numbers
    rather than requiring Plaid integration.

    Model: Mixtral-8x7B — good pattern recognition and categorization.
    """

    MODEL_TYPE = "analysis"

    # Industry benchmark spending percentages of gross income
    _BENCHMARKS = {
        "housing": 0.28, "food": 0.12, "transport": 0.10,
        "entertainment": 0.05, "subscriptions": 0.03, "health": 0.05,
        "shopping": 0.05, "utilities": 0.05, "other": 0.05,
    }

    def __init__(self):
        super().__init__(name="BehavioralPatternAgent", system_prompt=SYSTEM_PROMPT)

    def run(self, state: dict) -> dict:
        transactions = self._generate_mock_transactions(state)
        profile_summary = self._build_prompt(state, transactions)
        result = self._call_llm_json(profile_summary)

        return {**state, "behavioral_fingerprint": result}

    def _generate_mock_transactions(self, state: dict) -> list:
        """
        Generates 6 months of realistic mock transactions from the profile's
        income/expense figures. Deterministic from profile values for demo consistency.
        """
        income = state.get("monthly_income", 5000)
        expenses = state.get("monthly_expenses", 4000)

        # Distribute expenses across categories with slight randomness
        distribution = {
            "housing":       0.33,
            "food":          0.15,
            "transport":     0.12,
            "entertainment": 0.09,
            "subscriptions": 0.06,
            "health":        0.06,
            "shopping":      0.08,
            "utilities":     0.06,
            "other":         0.05,
        }

        transactions = []
        random.seed(int(income))  # deterministic for same profile
        months = ["2025-11", "2025-12", "2026-01", "2026-02", "2026-03", "2026-04"]

        for month in months:
            for category, pct in distribution.items():
                base = expenses * pct
                # Add small variance per month
                variance = base * random.uniform(-0.08, 0.12)
                amount = round(base + variance, 2)
                transactions.append({
                    "month": month, "category": category,
                    "amount": amount, "income": income,
                })

        return transactions

    def _build_prompt(self, state: dict, transactions: list) -> str:
        monthly_averages = {}
        counts = {}
        for t in transactions:
            cat = t["category"]
            monthly_averages[cat] = monthly_averages.get(cat, 0) + t["amount"]
            counts[cat] = counts.get(cat, 0) + 1

        for cat in monthly_averages:
            monthly_averages[cat] = round(monthly_averages[cat] / counts[cat], 2)

        benchmarks = {
            cat: round(state.get("monthly_income", 5000) * pct, 2)
            for cat, pct in self._BENCHMARKS.items()
        }

        return json.dumps({
            "monthly_income": state.get("monthly_income"),
            "monthly_expenses": state.get("monthly_expenses"),
            "average_monthly_spending_by_category": monthly_averages,
            "industry_benchmarks_for_income_level": benchmarks,
            "debts": state.get("debts", []),
        })
