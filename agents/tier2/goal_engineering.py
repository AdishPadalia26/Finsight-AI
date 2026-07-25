import json
from graph.nodes import BaseAgent
from tools.financial.calculator import (
    required_monthly_contribution,
    goal_feasibility_score,
    milestone_balances,
    total_minimum_debt_payments,
)

SYSTEM_PROMPT = """## ROLE
You are a certified financial planner (CFP) specializing in goal-based wealth planning. You analyze pre-computed goal feasibility data and produce structured, actionable goal roadmaps. You NEVER recalculate any numbers — they are authoritative and pre-computed in Python.

## ACTION
Given the pre-computed goal analysis, produce a complete goal roadmap with:
1. goals_analysis: for each goal — feasibility_tier (FEASIBLE / AT_RISK / INFEASIBLE), strategy_rationale (2-3 sentences explaining the approach), vehicle_recommendation (category only — never name tickers or banks), timeline_extension_needed (bool)
2. priority_order: ranked list of goal descriptions with reason for ranking
3. conflict_analysis: which goals conflict if total required > available; which to defer first
4. cross_goal_recommendation: 2-3 sentences on how to balance all goals simultaneously
5. quick_wins: 1-2 actions achievable in next 30 days to improve goal trajectory

## HARD CONSTRAINTS
- NEVER recalculate or modify any numeric value from the pre-computed data
- Vehicle categories only — never name specific ETFs, banks, brokers, or accounts by product name
- If funding_gap > 0, explicitly address it — do not gloss over it
- Feasibility < 50 = flag as INFEASIBLE; 50–79 = AT_RISK; 80+ = FEASIBLE
- Frame analysis as educational analysis, not licensed financial advice

## OUTPUT FORMAT
You MUST respond with ONLY a valid JSON object. No markdown, no bold text, no bullet points, no explanations outside the JSON.
Your entire response must be parseable by json.loads(). Do not include any text before or after the JSON object.

Begin your response with: {"""


class GoalEngineeringAgent(BaseAgent):
    """
    Agent 05 — Goal Engineering (Tier 2, Parallel)

    Precomputes required monthly contribution, feasibility score, and milestone
    balances for each goal using deterministic financial math. LLM then adds
    strategy rationale, vehicle recommendations, and conflict analysis.
    """

    MODEL_TYPE = "reasoning"
    PROVIDER = "nvidia"
    MODEL_ID = "moonshotai/kimi-k2.6"
    API_KEY_VAR = "NVIDIA_API_KEY_2"
    FALLBACK_PROVIDER = "groq"
    FALLBACK_MODEL_ID = "llama-3.3-70b-versatile"
    FALLBACK_API_KEY_VAR = "GROQ_API_KEY_3"
    MAX_TOKENS = 2048  # keep LLM output concise — computed_goals injected deterministically

    def __init__(self):
        super().__init__(name="GoalEngineeringAgent", system_prompt=SYSTEM_PROMPT)

    def run(self, state: dict) -> dict:
        income = state.get("monthly_income", 0)
        expenses = state.get("monthly_expenses", 0)
        savings_pool = state.get("savings", 0)
        risk = state.get("risk_tolerance", "moderate")
        goals = state.get("goals", [])
        debts = state.get("debts", [])

        min_debt_payments = total_minimum_debt_payments(debts)
        available_monthly = max(0.0, income - expenses - min_debt_payments)

        def _rate_for_goal(goal: dict) -> float:
            months = goal.get("timeline_months", 24)
            if months <= 24:
                return 0.045  # HYSA / T-bill equivalent
            if months <= 60:
                return 0.06   # balanced allocation
            return {"conservative": 0.055, "moderate": 0.08, "aggressive": 0.10}.get(risk, 0.08)

        computed_goals = []
        total_required_monthly = 0.0

        for goal in goals:
            target = float(goal.get("target_amount", 0))
            months = int(goal.get("timeline_months", 24))
            rate = _rate_for_goal(goal)

            req = required_monthly_contribution(target, savings_pool, months, annual_rate=rate)
            feasibility = goal_feasibility_score(req, available_monthly)
            milestones = milestone_balances(0.0, req, rate, months, checkpoints=4)

            months_cat = (
                "short_term" if months <= 24 else
                "medium_term" if months <= 60 else
                "long_term"
            )
            vehicle = (
                "high-yield savings or money market fund"
                if months <= 24 else
                "balanced index fund portfolio"
                if months <= 60 else
                (
                    "bond-heavy index fund portfolio" if risk == "conservative" else
                    "diversified equity index fund portfolio" if risk == "moderate" else
                    "growth-oriented equity index fund portfolio"
                )
            )

            computed_goals.append({
                "description": goal.get("description", ""),
                "priority": goal.get("priority", "medium"),
                "target_amount": target,
                "timeline_months": months,
                "timeline_category": months_cat,
                "assumed_annual_return_pct": round(rate * 100, 2),
                "required_monthly_contribution": req,
                "feasibility_score": feasibility,
                "milestone_balances": milestones,
                "recommended_vehicle_category": vehicle,
                "risk_flag": (
                    "INFEASIBLE" if feasibility < 50 else
                    "AT_RISK" if feasibility < 80 else
                    "FEASIBLE"
                ),
            })
            total_required_monthly += req

        funding_gap = max(0.0, round(total_required_monthly - available_monthly, 2))
        cross_goal = {
            "total_required_monthly": round(total_required_monthly, 2),
            "available_monthly_for_goals": round(available_monthly, 2),
            "funding_gap": funding_gap,
            "fully_funded": funding_gap == 0.0,
            "goals_at_risk": [g["description"] for g in computed_goals if g["feasibility_score"] < 80],
            "goals_infeasible": [g["description"] for g in computed_goals if g["feasibility_score"] < 50],
        }

        prompt_data = {
            "profile": {
                "monthly_income": income,
                "monthly_expenses": expenses,
                "available_monthly_for_goals": round(available_monthly, 2),
                "risk_tolerance": risk,
                "investment_horizon_years": state.get("investment_horizon"),
            },
            "computed_goals": computed_goals,
            "cross_goal_analysis": cross_goal,
        }

        try:
            result = self._call_llm_json(json.dumps(prompt_data))
        except (RuntimeError, ValueError) as e:
            print(f"[GoalEngineering] LLM unavailable — using fallback: {e}")
            result = {
                "goal_narrative": "LLM analysis unavailable — computed goal metrics are accurate.",
                "prioritization": [],
                "recommendations": [],
            }

        result["computed_goals"] = computed_goals
        result["cross_goal_summary"] = cross_goal

        return {**state, "goal_roadmap": result}
