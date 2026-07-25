import json
from graph.nodes import BaseAgent

# 2025 IRS contribution limits (hardcoded for demo; update annually)
_401K_LIMIT = 23500
_401K_CATCHUP_LIMIT = 31000   # age >= 50
_IRA_LIMIT = 7000
_IRA_CATCHUP_LIMIT = 8000     # age >= 50
_HSA_INDIVIDUAL_LIMIT = 4300
_HSA_FAMILY_LIMIT = 8550

# 2025 federal income tax brackets — single filer
_BRACKETS_SINGLE_2025 = [
    (11925,  0.10),
    (48475,  0.12),
    (103350, 0.22),
    (197300, 0.24),
    (250525, 0.32),
    (626350, 0.35),
    (float("inf"), 0.37),
]

SYSTEM_PROMPT = """## ROLE
You are a tax strategist specializing in personal income tax optimization. You analyze pre-computed tax metrics and produce actionable, US-centric tax optimization strategies. You NEVER recalculate numbers — they are pre-computed and authoritative.

## ACTION
Given the pre-computed tax analysis, produce:
1. tax_optimization_opportunities: list of opportunities, each with {name, annual_savings_potential, priority, explanation}
2. retirement_account_strategy: specific guidance on 401(k) / IRA / Roth IRA contribution approach for this profile
3. hsa_recommendation: whether HSA applies and how to use it
4. tax_loss_harvesting: whether applicable, why or why not
5. deadline_reminders: list of upcoming tax deadlines relevant to this profile
6. total_annual_savings_potential: sum all opportunity savings estimates
7. key_action: the single highest-impact tax move for this person

## HARD CONSTRAINTS
- NEVER reference specific tax software, financial advisors, or CPA firms by name
- All savings estimates come from pre-computed data — do NOT invent dollar amounts
- Always recommend consulting a CPA for complex situations (Roth conversions, etc.)
- Frame as educational analysis, not licensed tax advice
- Do NOT make up IRS rules — only use the hardcoded limits provided

## OUTPUT FORMAT
You MUST respond with ONLY a valid JSON object. No markdown, no bold text, no bullet points, no explanations outside the JSON.
Your entire response must be parseable by json.loads(). Do not include any text before or after the JSON object.

Begin your response with: {"""


def _marginal_bracket(annual_income: float) -> tuple:
    """Returns (marginal_rate, bracket_threshold) for single filer."""
    prev = 0
    for threshold, rate in _BRACKETS_SINGLE_2025:
        if annual_income <= threshold:
            return rate, threshold
        prev = threshold
    return 0.37, float("inf")


def _effective_tax_rate(annual_income: float) -> float:
    """Approximate effective rate using 2025 single brackets."""
    if annual_income <= 0:
        return 0.0
    total_tax = 0.0
    prev = 0.0
    for threshold, rate in _BRACKETS_SINGLE_2025:
        if annual_income <= threshold:
            total_tax += (annual_income - prev) * rate
            break
        total_tax += (threshold - prev) * rate
        prev = threshold
    return round(total_tax / annual_income * 100, 2)


class TaxIntelligenceAgent(BaseAgent):
    """
    Agent 07 — Tax Intelligence (Tier 2, Parallel)

    Precomputes marginal bracket, effective rate, and unused contribution room
    using 2025 IRS limits. LLM then produces actionable optimization strategies.
    """

    MODEL_TYPE = "reasoning"
    PROVIDER = "openrouter"
    MODEL_ID = "google/gemma-4-31b-it:free"
    API_KEY_VAR = "OPENROUTER_API_KEY_3"
    FALLBACK_PROVIDER = "gemini"
    FALLBACK_MODEL_ID = "gemini-2.5-flash"
    FALLBACK_API_KEY_VAR = None

    def __init__(self):
        super().__init__(name="TaxIntelligenceAgent", system_prompt=SYSTEM_PROMPT)

    def run(self, state: dict) -> dict:
        income = state.get("monthly_income", 0)
        annual_income = income * 12
        age = state.get("age", 35)
        investments = state.get("investments", 0)
        location = state.get("location", "")
        risk = state.get("risk_tolerance", "moderate")
        goals = state.get("goals", [])

        marginal_rate, _ = _marginal_bracket(annual_income)
        effective_rate = _effective_tax_rate(annual_income)
        catchup = age >= 50

        k401_limit = _401K_CATCHUP_LIMIT if catchup else _401K_LIMIT
        ira_limit = _IRA_CATCHUP_LIMIT if catchup else _IRA_LIMIT
        hsa_limit = _HSA_INDIVIDUAL_LIMIT  # assume individual

        # Conservative: assume no existing 401k contributions tracked
        unused_401k_room = k401_limit
        unused_ira_room = ira_limit

        # Rough tax savings potential
        k401_tax_savings = round(k401_limit * marginal_rate, 2)
        ira_tax_savings = round(ira_limit * marginal_rate * 0.5, 2)  # trad IRA, partial benefit
        hsa_tax_savings = round(hsa_limit * marginal_rate, 2)

        # Roth vs Traditional: Roth preferred if marginal < 24%
        roth_preferred = marginal_rate < 0.24

        # Tax-loss harvesting: applicable if investments > $10k
        tlh_applicable = investments > 10000

        # High-income state check (CA, NY, NJ)
        high_tax_state = any(st in (location or "") for st in ["CA", "New York", "NY", "NJ", "OR", "MN"])

        precomputed = {
            "annual_income_estimate": round(annual_income, 2),
            "marginal_bracket_pct": round(marginal_rate * 100, 2),
            "effective_rate_estimate_pct": effective_rate,
            "age": age,
            "catchup_contributions_eligible": catchup,
            "contribution_limits_2025": {
                "k401_annual_limit": k401_limit,
                "ira_annual_limit": ira_limit,
                "hsa_individual_limit": hsa_limit,
            },
            "unused_contribution_room": {
                "k401": unused_401k_room,
                "ira": unused_ira_room,
            },
            "estimated_tax_savings_potential": {
                "max_401k_deduction_benefit": k401_tax_savings,
                "ira_deduction_benefit_estimate": ira_tax_savings,
                "hsa_triple_advantage_savings": hsa_tax_savings,
            },
            "roth_vs_traditional": {
                "roth_preferred": roth_preferred,
                "rationale": (
                    "Current marginal rate below 24% — Roth likely better long-term"
                    if roth_preferred else
                    "Higher marginal rate — pre-tax Traditional IRA/401k deduction more valuable now"
                ),
            },
            "tax_loss_harvesting": {
                "applicable": tlh_applicable,
                "rationale": (
                    f"Portfolio of ${investments:,.0f} is large enough to implement TLH strategy"
                    if tlh_applicable else
                    "Portfolio too small for meaningful TLH benefit at current size"
                ),
            },
            "high_tax_state_detected": high_tax_state,
            "location": location,
            "goals": [g.get("description") for g in goals],
        }

        try:
            result = self._call_llm_json(json.dumps(precomputed))
        except (RuntimeError, ValueError) as e:
            print(f"[TaxIntelligence] LLM unavailable — using fallback: {e}")
            result = {
                "opportunities": [],
                "summary": "LLM analysis unavailable — pre-computed tax metrics are accurate.",
                "total_annual_savings_potential": round(
                    precomputed["estimated_tax_savings_potential"]["max_401k_deduction_benefit"]
                    + precomputed["estimated_tax_savings_potential"]["ira_deduction_benefit_estimate"]
                    + precomputed["estimated_tax_savings_potential"]["hsa_triple_advantage_savings"],
                    2,
                ),
            }

        result["precomputed_metrics"] = precomputed

        # Inject deterministic metrics at top level so consumers don't need to traverse precomputed_metrics
        result["marginal_bracket_pct"] = precomputed["marginal_bracket_pct"]
        result["effective_rate_pct"] = precomputed["effective_rate_estimate_pct"]
        result["roth_preferred"] = roth_preferred

        # Compute total_annual_savings_potential from opportunities if LLM didn't set it
        if "total_annual_savings_potential" not in result:
            opportunities = result.get("opportunities") or result.get("tax_optimization_opportunities") or []
            total = sum(
                op.get("annual_savings", 0) or op.get("annual_savings_potential", 0)
                for op in opportunities
            )
            result["total_annual_savings_potential"] = round(total, 2)

        # Normalize opportunities key — ensure both keys exist for different consumers
        if "tax_optimization_opportunities" in result and "opportunities" not in result:
            result["opportunities"] = result["tax_optimization_opportunities"]
        elif "opportunities" in result and "tax_optimization_opportunities" not in result:
            result["tax_optimization_opportunities"] = result["opportunities"]

        return {**state, "tax_opportunities": result}
