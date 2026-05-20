import json
from graph.nodes import BaseAgent

SYSTEM_PROMPT = """## ROLE
You are an adversarial financial stress-tester. Your job is NOT to be helpful — it is to find every weakness in a financial plan and force it to be stronger. You are the last line of defense before a real person acts on this advice. Do not soften your critique. A score of 7+ means the plan genuinely survives that scenario — it should be hard to earn.

## ACTION
Stress-test the combined financial plan against exactly these 5 scenarios. You must score ALL 5 — never skip one:
1. JOB_LOSS: User loses ALL primary income for 6 months
2. MARKET_CRASH: Investment portfolio drops 30% in value within 3 months
3. MEDICAL_EMERGENCY: Unexpected out-of-pocket expense of $50,000
4. RATE_SPIKE: All variable interest rates rise by 3 percentage points
5. INFLATION_SPIKE: Inflation rises to 8% for 12 months, increasing all living costs

For EACH scenario:
- Score plan resilience 1–10 (1 = plan fails catastrophically, 10 = survives easily)
- Identify the specific vulnerability with exact dollar amounts where possible (e.g., "Emergency fund covers only 1.4 months — gap of $14,000 to reach 3-month minimum")
- Suggest the minimum change that would improve the score by at least 2 points

Overall assessment rules:
- If ANY score < 7: set status to "NEEDS_REVISION", list agents_to_revise (budget_architect and/or investment_strategist)
- If ALL scores >= 7: set status to "STRESS_TESTED_APPROVED"
- If revision_count >= 3: set status to "ACCEPTED_WITH_CAVEATS" regardless of scores

## CONTEXT
You receive the full combined output of budget_architect, investment_strategist, and profile context. Look for: insufficient emergency fund, over-leveraged debt, portfolio concentration risk, optimistic income assumptions, under-insured scenarios.

## HARD CONSTRAINTS — Never violate these
- You MUST score all 5 scenarios — no skipping
- A score of 7+ means the plan genuinely handles that scenario well
- Be specific — cite exact dollar amounts and months from the plan data
- Do not recommend specific stocks, tickers, or financial products
- Do not soften findings — be direct about weaknesses

## Think adversarially — for each scenario ask:
1. What breaks first in this plan under this scenario?
2. How many months until the user runs out of money or defaults?
3. What is the minimum change to the budget or investment plan that fixes this?

## OUTPUT FORMAT
You MUST respond with ONLY a valid JSON object. No markdown, no bold text, no bullet points, no explanations outside the JSON.
Your entire response must be parseable by json.loads(). Do not include any text before or after the JSON object.

Begin your response with: {"""


class CriticAgent(BaseAgent):
    """
    Agent 10 — Critic / Red Team (Tier 3, Sequential)

    Adversarially stress-tests the combined plan from Tier 2.
    Scores resilience across 5 scenarios. If any score < 7 AND revision_count < 3,
    the LangGraph workflow routes back to Tier 2 agents for revision.

    The revision loop logic lives in graph/workflow.py as a conditional edge —
    this agent only scores and flags; it does not trigger the loop itself.

    Model: Llama-3.3-70B — latest Llama, best adversarial and critical reasoning.
    """

    MODEL_TYPE = "adversarial"
    PROVIDER = "gemini"
    MODEL_ID = "gemini-2.0-flash"
    API_KEY_VAR = None
    FALLBACK_PROVIDER = "groq"
    FALLBACK_MODEL_ID = "llama-3.3-70b-versatile"
    FALLBACK_API_KEY_VAR = "GROQ_API_KEY_1"
    MAX_TOKENS = 2048  # critic output is structured JSON — keep concise

    def __init__(self):
        super().__init__(name="CriticAgent", system_prompt=SYSTEM_PROMPT)

    def run(self, state: dict) -> dict:
        revision_count = state.get("revision_count", 0)

        # If already at max revisions, force acceptance
        if revision_count >= 3:
            return {
                **state,
                "critic_scores": {
                    "status": "ACCEPTED_WITH_CAVEATS",
                    "note": f"Accepted after {revision_count} revision iterations",
                    "revision_count": revision_count,
                },
            }

        combined_plan = {
            "budget_recommendation": state.get("budget_recommendation"),
            "investment_strategy": state.get("investment_strategy"),
            "goal_roadmap": state.get("goal_roadmap"),
            "tax_opportunities": state.get("tax_opportunities"),
            "debt_roadmap": state.get("debt_roadmap"),
            "profile_context": {
                "age": state.get("age"),
                "monthly_income": state.get("monthly_income"),
                "monthly_expenses": state.get("monthly_expenses"),
                "savings": state.get("savings"),
                "investments": state.get("investments"),
                "debts": state.get("debts", []),
                "risk_tolerance": state.get("risk_tolerance"),
            },
            "revision_count": revision_count,
        }

        try:
            result = self._call_llm_json(json.dumps(combined_plan))
        except (RuntimeError, ValueError) as e:
            print(f"[Critic] LLM unavailable — accepting plan with caveat: {e}")
            result = {
                "status": "ACCEPTED_WITH_CAVEATS",
                "overall_score": 70,
                "critique": "LLM critic unavailable — plan accepted without adversarial review.",
                "flags": [],
                "revision_needed": False,
            }

        result["revision_count"] = revision_count

        return {**state, "critic_scores": result}
