import json
from graph.nodes import BaseAgent
from tools.data.market_data import get_market_snapshot, format_for_prompt
from tools.safety.output_scanner import scan_output

SYSTEM_PROMPT = """You are the Investment Strategist Agent for FinSight AI.

Recommend an asset allocation strategy based on the user's risk profile, investment horizon, and goals.
Your recommendations MUST be grounded in the live market data provided.

Produce:
1. Recommended asset allocation: % stocks, % bonds, % cash, % alternatives (must sum to 100%)
2. ETF CATEGORY recommendations — describe asset class categories only (e.g., "broad US equity index funds", "international developed markets ETFs", "short-duration bond funds"). NEVER name specific tickers.
3. Account type optimization — what asset types belong in 401k vs Roth IRA vs taxable brokerage
4. Market context — explain how today's specific rates/inflation justify this recommendation
5. Rebalancing guidance — how often and what triggers a rebalance

HARD CONSTRAINTS — violations will block your output:
- NEVER recommend specific individual stocks (no company names)
- NEVER recommend specific cryptocurrencies
- NEVER use "guaranteed", "will definitely", "certain return", "risk-free"
- NEVER name specific ETF tickers (SPY, VTI, etc.) — describe the category only
- Always note that past performance does not guarantee future results

STRICT OUTPUT RULES:
- Output ONLY a valid JSON object. No explanation, no markdown, no preamble.
- Start your response with { and end with }

Required JSON structure:
{
  "allocation": {
    "us_equities_pct": <float>, "international_equities_pct": <float>,
    "bonds_pct": <float>, "cash_pct": <float>, "alternatives_pct": <float>
  },
  "allocation_rationale": <string>,
  "etf_categories": [
    {"asset_class": <string>, "allocation_pct": <float>, "rationale": <string>}
  ],
  "account_optimization": {
    "tax_advantaged_401k": <string>,
    "roth_ira": <string>,
    "taxable_brokerage": <string>
  },
  "market_context": <string>,
  "rebalancing_guidance": <string>,
  "risk_alignment": <string>
}"""


class InvestmentStrategistAgent(BaseAgent):
    """
    Agent 06 — Investment Strategist (Tier 2, Parallel)

    Pulls live market data (yfinance + FRED) before calling LLM.
    Runs its own post-LLM compliance scan (defense-in-depth) to catch
    any ticker or guaranteed-return language before output leaves this agent.

    Model: Llama-3.1-70B — complex reasoning over real market data.
    """

    MODEL_TYPE = "reasoning"

    def __init__(self):
        super().__init__(name="InvestmentStrategistAgent", system_prompt=SYSTEM_PROMPT)

    def run(self, state: dict) -> dict:
        # Pull live data first — handle None gracefully
        snapshot = get_market_snapshot()
        market_text = format_for_prompt(snapshot)

        prompt_data = {
            "live_market_data": market_text,
            "investor_profile": {
                "age": state.get("age"),
                "risk_tolerance": state.get("risk_tolerance"),
                "investment_horizon_years": state.get("investment_horizon"),
                "current_investments": state.get("investments", 0),
                "monthly_investable_surplus": round(
                    state.get("monthly_income", 0) - state.get("monthly_expenses", 0), 2
                ),
                "goals": state.get("goals", []),
            },
            "budget_context": {
                "savings_rate": state.get("budget_recommendation", {}).get(
                    "monthly_allocations", {}
                ) if state.get("budget_recommendation") else {},
            },
        }

        raw_result = self._call_llm_json(json.dumps(prompt_data))

        # Defense-in-depth: scan this agent's output before it leaves
        text_to_scan = json.dumps(raw_result)
        scan = scan_output(text_to_scan)
        if scan["severity"] == "CRITICAL":
            raise ValueError(
                f"InvestmentStrategist produced CRITICAL compliance violation: "
                f"{scan['violations']}"
            )

        return {**state, "investment_strategy": raw_result}
