import json
from graph.nodes import BaseAgent
from tools.data import market_data
from tools.financial.calculator import savings_rate, debt_to_income, emergency_fund_months, total_minimum_debt_payments

SYSTEM_PROMPT = """## ROLE
You are a senior personal financial advisor who synthesizes outputs from an entire multi-agent financial planning system into a single, coherent, highly-personalised advisory narrative. You have access to the person's full financial picture — budget, investments, goals, debts, taxes, life events, stress tests, and behavioral data. You identify cross-domain interactions and interactions that individual specialists would miss.

## ACTION
Produce a comprehensive personalised advisory package with:
1. executive_summary: 3–4 sentences capturing the person's financial situation, biggest strength, and most urgent priority
2. financial_health_narrative: 1–2 paragraphs describing what the numbers say about their financial life stage and trajectory
3. cross_domain_insights: list of 3–5 insights that span multiple domains (e.g., "Your credit card debt at 22.9% APR is costing more than your investment portfolio is likely earning — debt elimination takes priority over investing until the card is cleared")
4. priority_actions: ranked list of actions (1 = highest priority), each with:
   - rank, action, domain, rationale, timeline, estimated_monthly_impact
5. wealth_building_roadmap: phased plan across 3 phases (near_term: 0–12mo, mid_term: 1–3yr, long_term: 3+yr), each with focus areas and milestones
6. key_risks: list of 2–4 financial risks specific to this person with mitigation strategies
7. personalised_insights: 2–3 insights unique to this person's specific combination of data (not generic advice)
8. benchmark_comparison: how this person compares to typical benchmarks for their age/income (savings rate, emergency fund, DTI, net worth)
9. next_30_day_checklist: list of 5 concrete actions achievable in the next 30 days, each as a string

## MANDATORY CROSS-DOMAIN ANALYSIS
Before writing, identify:
- Does high-rate debt make investing mathematically suboptimal?
- Is emergency fund adequate relative to job-loss stress test runway?
- Can goal timelines be met with current savings rate and surplus?
- Does tax optimization opportunity (401k, HSA) materially affect net income?
- Do life events change goal priorities?
- What does the market regime imply for asset allocation timing?

## HARD CONSTRAINTS
- NEVER recommend specific stocks, tickers, banks, insurance companies, or financial advisors
- NEVER imply guaranteed returns or risk-free strategies
- All dollar amounts must be derivable from the provided data
- Frame as analysis and educational guidance, not licensed financial advice
- Include disclaimer: "This analysis is for educational purposes only and does not constitute licensed financial, tax, or legal advice"

## OUTPUT FORMAT
You MUST respond with ONLY a valid JSON object. No markdown, no bold text, no bullet points, no explanations outside the JSON.
Your entire response must be parseable by json.loads(). Do not include any text before or after the JSON object.

Begin your response with: {"""


class PersonalisedAdvisorAgent(BaseAgent):
    """
    Agent — Personalised Advisor (Tier 3, Sequential, after life_event and before critic)

    Receives the entire state including all Tier 1 and Tier 2 agent outputs,
    stress tests, and life events. Synthesizes into cross-domain holistic advice.
    This is the premium intelligence layer of the platform.
    """

    MODEL_TYPE = "reasoning"
    PROVIDER = "gemini"
    MODEL_ID = "gemini-2.5-flash"
    API_KEY_VAR = None
    FALLBACK_PROVIDER = "groq"
    FALLBACK_MODEL_ID = "llama-3.3-70b-versatile"
    FALLBACK_API_KEY_VAR = "GROQ_API_KEY_2"
    MAX_TOKENS = 2200

    def __init__(self):
        super().__init__(name="PersonalisedAdvisorAgent", system_prompt=SYSTEM_PROMPT)

    def run(self, state: dict) -> dict:
        income = state.get("monthly_income", 0)
        expenses = state.get("monthly_expenses", 0)
        savings = state.get("savings", 0)
        investments = state.get("investments", 0)
        property_value = state.get("property_value", 0)
        debts = state.get("debts", [])
        age = state.get("age")
        risk = state.get("risk_tolerance")
        horizon = state.get("investment_horizon")

        min_debt = total_minimum_debt_payments(debts)
        sr = savings_rate(income, expenses)
        dti = debt_to_income(min_debt, income)
        em = emergency_fund_months(savings, expenses)
        surplus = round(income - expenses, 2)
        net_worth_approx = round((savings + investments + property_value) - sum(d.get("balance", 0) for d in debts), 2)

        budget = state.get("budget_recommendation") or {}
        investment = state.get("investment_strategy") or {}
        goals = state.get("goal_roadmap") or {}
        debt_plan = state.get("debt_roadmap") or {}
        tax = state.get("tax_opportunities") or {}
        life_events = state.get("life_events") or {}
        stress = state.get("stress_tests") or {}
        behavioral = state.get("behavioral_fingerprint") or {}

        # Live market context for regime analysis. This should never block the
        # advisor from producing a response.
        try:
            snapshot = market_data.get_full_market_snapshot()
            market_text = market_data.format_full_snapshot_for_prompt(snapshot)
        except Exception as e:
            print(f"[PersonalisedAdvisor] Market snapshot unavailable: {e}")
            market_text = "Live market data unavailable; use profile metrics and specialist outputs."

        # Age-based benchmarks
        benchmark_net_worth = income * 12 * max(1, (age or 30) - 25) * 0.1  # rough rule of thumb
        benchmark_savings_rate = 20.0
        benchmark_emergency_months = 6.0
        benchmark_dti = 36.0

        prompt_data = {
            "financial_overview": {
                "age": age,
                "location": state.get("location"),
                "risk_tolerance": risk,
                "investment_horizon_years": horizon,
                "monthly_income": income,
                "monthly_expenses": expenses,
                "monthly_surplus": surplus,
                "savings_rate_pct": sr,
                "debt_to_income_pct": dti,
                "emergency_fund_months": em,
                "net_worth": net_worth_approx,
                "savings": savings,
                "investments": investments,
                "property_value": property_value,
                "total_debt": round(sum(d.get("balance", 0) for d in debts), 2),
                "debt_types": [d.get("type") for d in debts if d.get("balance", 0) > 0],
            },
            "benchmarks": {
                "savings_rate_benchmark_pct": benchmark_savings_rate,
                "emergency_fund_benchmark_months": benchmark_emergency_months,
                "dti_benchmark_pct": benchmark_dti,
                "net_worth_benchmark_estimate": round(benchmark_net_worth, 2),
                "user_vs_benchmark": {
                    "savings_rate": "above" if sr >= benchmark_savings_rate else "below",
                    "emergency_fund": "above" if em >= benchmark_emergency_months else "below",
                    "dti": "healthy" if dti <= benchmark_dti else "elevated",
                    "net_worth": "above" if net_worth_approx >= benchmark_net_worth else "below",
                },
            },
            "planning_outputs": {
                "budget_health_score": (budget.get("health_score") or {}).get("total") if budget else None,
                "budget_framework": budget.get("recommended_framework") if budget else None,
                "investment_allocation": investment.get("allocation") if investment else None,
                "investment_risk_alignment": investment.get("risk_alignment") if investment else None,
                "goal_funding_gap": (goals.get("cross_goal_summary") or {}).get("funding_gap") if goals else None,
                "goals_at_risk": (goals.get("cross_goal_summary") or {}).get("goals_at_risk", []) if goals else [],
                "debt_recommended_method": debt_plan.get("recommended_method") if debt_plan else None,
                "debt_months_to_freedom": (debt_plan.get("simulations") or {}).get(
                    debt_plan.get("recommended_method", "avalanche"), {}
                ).get("months_to_debt_free") if debt_plan else None,
                "tax_total_savings_potential": tax.get("total_annual_savings_potential") if tax else None,
            },
            "life_events": life_events,
            "stress_tests": stress,
            "behavioral_fingerprint": {
                "discipline_score": behavioral.get("discipline_score"),
                "key_insight": behavioral.get("key_insight"),
            } if behavioral else None,
            "live_market_context": market_text,
        }

        try:
            result = self._call_llm_json(json.dumps(prompt_data))
        except (RuntimeError, ValueError) as e:
            print(f"[PersonalisedAdvisor] LLM unavailable - using deterministic fallback: {e}")
            result = self._fallback_advice(
                income=income,
                expenses=expenses,
                savings=savings,
                investments=investments,
                debts=debts,
                age=age,
                risk=risk,
                horizon=horizon,
                savings_rate_pct=sr,
                dti_pct=dti,
                emergency_months=em,
                surplus=surplus,
                net_worth=net_worth_approx,
                benchmark_net_worth=round(benchmark_net_worth, 2),
            )
        if not isinstance(result.get("benchmark_comparison"), str):
            result["benchmark_comparison"] = json.dumps(result.get("benchmark_comparison")) if result.get("benchmark_comparison") else ""
        if not isinstance(result.get("executive_summary"), str):
            result["executive_summary"] = json.dumps(result.get("executive_summary")) if result.get("executive_summary") else ""
        if not isinstance(result.get("financial_health_narrative"), str):
            result["financial_health_narrative"] = json.dumps(result.get("financial_health_narrative")) if result.get("financial_health_narrative") else ""
        return {**state, "personalised_advice": result}

    @staticmethod
    def _fallback_advice(
        *,
        income: float,
        expenses: float,
        savings: float,
        investments: float,
        debts: list,
        age,
        risk,
        horizon,
        savings_rate_pct: float,
        dti_pct: float,
        emergency_months: float,
        surplus: float,
        net_worth: float,
        benchmark_net_worth: float,
    ) -> dict:
        high_rate_debts = [
            d for d in debts
            if d.get("balance", 0) > 0 and d.get("interest_rate", 0) >= 8
        ]
        total_debt = round(sum(d.get("balance", 0) for d in debts), 2)
        emergency_target = round(expenses * 6, 2)
        emergency_gap = max(0, round(emergency_target - savings, 2))
        savings_rate_label = "strong" if savings_rate_pct >= 20 else "needs improvement"
        debt_label = "healthy" if dti_pct <= 36 else "elevated"

        actions = []
        rank = 1
        if high_rate_debts:
            top_debt = max(high_rate_debts, key=lambda d: d.get("interest_rate", 0))
            actions.append({
                "rank": rank,
                "action": f"Pay extra toward {top_debt.get('type', 'high-rate debt')} before increasing investing",
                "domain": "debt",
                "rationale": f"{top_debt.get('interest_rate', 0)}% interest is likely higher than expected portfolio returns.",
                "timeline": "Start this month",
                "estimated_monthly_impact": round(min(max(surplus, 0), top_debt.get("balance", 0)), 2),
            })
            rank += 1
        if emergency_months < 6:
            monthly_target = round(min(max(surplus * 0.5, 100), emergency_gap), 2) if emergency_gap else 0
            actions.append({
                "rank": rank,
                "action": f"Build emergency savings toward ${emergency_target:,.0f}",
                "domain": "savings",
                "rationale": f"Current runway is about {emergency_months:.1f} months; target is 6 months.",
                "timeline": "Next 6-12 months",
                "estimated_monthly_impact": monthly_target,
            })
            rank += 1
        if surplus > 0:
            actions.append({
                "rank": rank,
                "action": "Automate monthly surplus into goals, debt payoff, or diversified investments",
                "domain": "budget",
                "rationale": f"Monthly surplus is about ${surplus:,.0f}; automation reduces drift.",
                "timeline": "Within 30 days",
                "estimated_monthly_impact": round(surplus, 2),
            })
            rank += 1
        actions.append({
            "rank": rank,
            "action": "Review investment allocation for risk tolerance and time horizon",
            "domain": "investment",
            "rationale": f"Profile risk is {risk or 'unspecified'} with a {horizon or 'long-term'} year horizon.",
            "timeline": "This quarter",
            "estimated_monthly_impact": "Risk control, not guaranteed return",
        })

        return {
            "executive_summary": (
                f"Your profile shows ${income:,.0f} monthly income, ${expenses:,.0f} expenses, "
                f"and a {savings_rate_pct:.1f}% savings rate. The most urgent priority is "
                f"{'high-rate debt' if high_rate_debts else 'emergency-fund depth' if emergency_months < 6 else 'consistent wealth building'}. "
                "This analysis is for educational purposes only and does not constitute licensed financial, tax, or legal advice"
            ),
            "financial_health_narrative": (
                f"You have about ${net_worth:,.0f} estimated net worth, ${investments:,.0f} invested, "
                f"and ${total_debt:,.0f} in debt. Savings rate is {savings_rate_label}; debt-to-income is {debt_label} at {dti_pct:.1f}%."
            ),
            "cross_domain_insights": [
                "Emergency savings, debt payoff, and investing should be sequenced by risk and interest rate.",
                f"Your monthly surplus of about ${surplus:,.0f} is the main lever for the next plan cycle.",
                "Avoid increasing investment risk until cash runway and high-rate debt are under control." if high_rate_debts or emergency_months < 6 else "With core protections in place, periodic rebalancing and goal automation matter most.",
            ],
            "priority_actions": actions,
            "wealth_building_roadmap": {
                "near_term": {
                    "focus": "Stabilize cash flow and immediate risks",
                    "milestones": ["Reach at least 3 months of expenses saved", "Automate the top priority action"],
                },
                "mid_term": {
                    "focus": "Move from stability to compounding",
                    "milestones": ["Reach 6-month emergency reserve", "Review goal funding monthly"],
                },
                "long_term": {
                    "focus": "Compound wealth consistently",
                    "milestones": ["Maintain diversified allocation", "Revisit plan after major life or income changes"],
                },
            },
            "key_risks": [
                {"risk": "Cash-flow shock", "mitigation": f"Build emergency savings toward ${emergency_target:,.0f}."},
                {"risk": "Plan drift", "mitigation": "Automate transfers and review progress every month."},
            ],
            "personalised_insights": [
                f"Your emergency fund covers about {emergency_months:.1f} months of expenses.",
                f"Estimated net worth is {'above' if net_worth >= benchmark_net_worth else 'below'} a rough age-income benchmark.",
            ],
            "benchmark_comparison": (
                f"Savings rate: {savings_rate_pct:.1f}% vs 20% benchmark; emergency fund: "
                f"{emergency_months:.1f} months vs 6 months; DTI: {dti_pct:.1f}% vs 36% benchmark."
            ),
            "next_30_day_checklist": [
                {"step": "Confirm all monthly expenses and debt minimums are current", "description": "Clean inputs improve the plan.", "deadline": "7 days"},
                {"step": "Set one automatic transfer for the highest-ranked action", "description": "Use the monthly surplus intentionally.", "deadline": "14 days"},
                {"step": "Review emergency fund target", "description": f"Target ${emergency_target:,.0f} for 6 months of expenses.", "deadline": "30 days"},
                {"step": "Check investment allocation against risk tolerance", "description": "Rebalance only if materially off target.", "deadline": "30 days"},
                {"step": "Schedule next monthly plan review", "description": "Track progress and update assumptions.", "deadline": "30 days"},
            ],
        }
