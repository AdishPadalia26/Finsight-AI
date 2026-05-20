import json
from graph.nodes import BaseAgent
from tools.financial.calculator import total_debt_balance

SYSTEM_PROMPT = """## ROLE
You are a financial life planning expert who identifies upcoming lifecycle events that will materially impact a person's finances. You detect these from profile data (age, goals, debt mix, income trajectory) and provide actionable preparation guidance.

## ACTION
Based on the financial profile, planning outputs, and life signals provided, produce:
1. events: list of anticipated life events, each with:
   - event_name: clear name (e.g., "Home Purchase", "Career Transition", "Retirement Planning Acceleration")
   - probability: "HIGH" / "MODERATE" / "SPECULATIVE"
   - estimated_timeline: e.g., "6–18 months", "2–3 years", "5–7 years"
   - financial_impact_estimate: rough dollar range or monthly impact
   - preparation_actions: 2–3 specific, numbered preparation steps
   - insurance_flag: whether life/disability/umbrella insurance review is warranted (bool)
   - estate_planning_flag: whether will/trust/beneficiary review is warranted (bool)
2. summary_narrative: 2 sentences on the overall life stage and biggest financial inflection point ahead
3. priority_event: the single highest-priority event to prepare for

## SIGNAL DETECTION GUIDE
- Age 25–35 + moderate income → likely home purchase, marriage, family formation
- Age 30–45 + mortgage + children goals → education funding, insurance needs
- Age 45–55 + retirement goal → acceleration, catch-up contributions, sequence risk
- Age 55+ + retirement goal < 10 years → Medicare planning, Social Security optimization, legacy
- High credit card debt → risk of financial stress event, job change
- Large goals with tight feasibility → likely need to increase income or defer timeline

## HARD CONSTRAINTS
- Do NOT make up financial figures — use only data provided
- Flag estate planning only for age 40+ or when dependents are implied
- Do NOT recommend specific insurance companies or financial products by name
- Frame as analysis and preparation guidance, not licensed advice

## OUTPUT FORMAT
You MUST respond with ONLY a valid JSON object. No markdown, no bullet points, no explanations outside the JSON.
Your entire response must be parseable by json.loads(). Do not include any text before or after the JSON.

Begin your response with: {"""


class LifeEventAgent(BaseAgent):
    """
    Agent 09 — Life Event Anticipation (Tier 3, Sequential)

    Detects likely upcoming financial lifecycle events from profile signals
    (age, goals, debt mix, income) and generates preparation guidance.
    """

    MODEL_TYPE = "reasoning"
    PROVIDER = "nvidia"
    MODEL_ID = "nvidia/llama-3.3-nemotron-super-49b-v1"
    API_KEY_VAR = "NVIDIA_API_KEY_1"
    FALLBACK_PROVIDER = "gemini"
    FALLBACK_MODEL_ID = "gemini-2.5-flash"
    FALLBACK_API_KEY_VAR = None

    def __init__(self):
        super().__init__(name="LifeEventAgent", system_prompt=SYSTEM_PROMPT)

    def run(self, state: dict) -> dict:
        age = state.get("age", 30)
        goals = state.get("goals", [])
        debts = state.get("debts", [])
        income = state.get("monthly_income", 0)
        expenses = state.get("monthly_expenses", 0)
        savings = state.get("savings", 0)
        investments = state.get("investments", 0)
        risk = state.get("risk_tolerance", "moderate")
        horizon = state.get("investment_horizon", 10)
        location = state.get("location", "")
        budget = state.get("budget_recommendation") or {}
        goal_roadmap = state.get("goal_roadmap") or {}

        total_debt = total_debt_balance(debts)
        debt_types = [d.get("type", "") for d in debts if d.get("balance", 0) > 0]
        has_mortgage = "mortgage" in debt_types
        has_student_loan = "student_loan" in debt_types
        high_credit_card = any(
            d.get("type") == "credit_card" and d.get("balance", 0) > 5000
            for d in debts
        )

        goal_keywords = " ".join(g.get("description", "").lower() for g in goals)
        has_home_goal = any(w in goal_keywords for w in ["home", "house", "down payment", "property"])
        has_retire_goal = any(w in goal_keywords for w in ["retire", "retirement"])
        has_education_goal = any(w in goal_keywords for w in ["education", "college", "school"])
        has_emergency_goal = any(w in goal_keywords for w in ["emergency", "fund"])

        life_stage = (
            "early_career" if age < 30 else
            "mid_career" if age < 45 else
            "late_career" if age < 55 else
            "pre_retirement"
        )

        prompt_data = {
            "profile": {
                "age": age,
                "life_stage": life_stage,
                "location": location,
                "monthly_income": income,
                "monthly_expenses": expenses,
                "monthly_surplus": round(income - expenses, 2),
                "savings": savings,
                "investments": investments,
                "risk_tolerance": risk,
                "investment_horizon_years": horizon,
                "total_debt": total_debt,
            },
            "signals": {
                "debt_types_active": debt_types,
                "has_mortgage": has_mortgage,
                "has_student_loan": has_student_loan,
                "high_credit_card_balance": high_credit_card,
                "goal_signals": {
                    "home_purchase_likely": has_home_goal or (age < 35 and not has_mortgage),
                    "retirement_planning_active": has_retire_goal,
                    "education_funding_likely": has_education_goal or (30 < age < 45),
                    "emergency_fund_building": has_emergency_goal,
                },
            },
            "planning_context": {
                "health_score": (budget.get("health_score") or {}).get("total") if budget else None,
                "goals": [
                    {"description": g.get("description"), "timeline_months": g.get("timeline_months"), "priority": g.get("priority")}
                    for g in goals
                ],
                "goal_funding_gap": (goal_roadmap.get("cross_goal_summary") or {}).get("funding_gap") if goal_roadmap else None,
            },
        }

        try:
            result = self._call_llm_json(json.dumps(prompt_data))
        except (RuntimeError, ValueError) as e:
            print(f"[LifeEvent] LLM unavailable — using fallback: {e}")
            result = {
                "events": [],
                "recommendations": ["LLM analysis unavailable — life stage detected deterministically."],
            }

        # Inject deterministic fields that the LLM never computes
        result["life_stage"] = life_stage

        # Normalize events list — LLM may use event_name or event key
        raw_events = result.get("events") or []
        normalized_events = []
        for evt in raw_events:
            if isinstance(evt, dict):
                raw_name = evt.get("event_name") or evt.get("event") or "UNKNOWN"
                evt["event"] = raw_name.upper().replace(" ", "_")
                normalized_events.append(evt)
        result["events"] = normalized_events

        return {**state, "life_events": result}
