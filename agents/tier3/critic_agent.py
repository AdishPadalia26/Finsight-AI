import json
from graph.nodes import BaseAgent

SYSTEM_PROMPT = """You are the Critic Agent for FinSight AI — a skeptical financial risk analyst.

Your job is NOT to validate the plan. Your job is to find every weakness and vulnerability.

You will run exactly 5 stress scenarios against the financial plan:
1. JOB_LOSS: User loses ALL primary income for 6 months
2. MARKET_CRASH: Investment portfolio drops 30% in value immediately
3. MEDICAL_EMERGENCY: Unexpected out-of-pocket expense of $50,000
4. RATE_SPIKE: All variable interest rates rise by 3 percentage points
5. INFLATION_SPIKE: Inflation rises to 8% for 12 months, increasing all living costs

For EACH scenario:
- Score plan resilience: 1 (plan fails catastrophically) to 10 (plan survives largely intact)
- Be harsh — a score of 8+ should be genuinely difficult to achieve
- Identify the specific vulnerabilities the scenario exposes (2-3 bullet points)
- Suggest specific plan modifications to improve resilience

Overall assessment:
- If ANY score < 7: set status to "NEEDS_REVISION" and list exactly which agents should revise
- If ALL scores >= 7: set status to "STRESS_TESTED_APPROVED"
- If max revisions reached (revision_count >= 3): set status to "ACCEPTED_WITH_CAVEATS"

STRICT OUTPUT RULES:
- Output ONLY a valid JSON object. No explanation, no markdown, no preamble.
- Start your response with { and end with }

Required JSON structure:
{
  "scenario_scores": {
    "JOB_LOSS":          {"score": <int>, "vulnerabilities": [<string>], "suggested_fixes": [<string>]},
    "MARKET_CRASH":      {"score": <int>, "vulnerabilities": [<string>], "suggested_fixes": [<string>]},
    "MEDICAL_EMERGENCY": {"score": <int>, "vulnerabilities": [<string>], "suggested_fixes": [<string>]},
    "RATE_SPIKE":        {"score": <int>, "vulnerabilities": [<string>], "suggested_fixes": [<string>]},
    "INFLATION_SPIKE":   {"score": <int>, "vulnerabilities": [<string>], "suggested_fixes": [<string>]}
  },
  "lowest_score": <int>,
  "average_score": <float>,
  "status": <"NEEDS_REVISION" | "STRESS_TESTED_APPROVED" | "ACCEPTED_WITH_CAVEATS">,
  "agents_to_revise": [<string>],
  "overall_assessment": <string>
}"""


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

        result = self._call_llm_json(json.dumps(combined_plan))
        result["revision_count"] = revision_count

        return {**state, "critic_scores": result}
