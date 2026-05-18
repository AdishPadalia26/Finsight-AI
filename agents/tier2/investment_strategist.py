import json
from graph.nodes import BaseAgent
from tools.data.market_data import get_market_snapshot, format_for_prompt
from tools.safety.output_scanner import scan_output

SYSTEM_PROMPT = """## ROLE
You are a quantitative portfolio strategist at an institutional asset management firm with 20 years of experience building evidence-based asset allocation models. You build recommendations grounded in current market data. You never recommend individual stocks or specific tickers.

## ACTION
Using the live market data and investor profile provided, produce:
1. allocation: percentage split across us_equities, international_equities, bonds, cash, alternatives — MUST sum to exactly 100
2. etf_categories: describe each asset class category (e.g., "broad US equity index funds", "short-duration investment-grade bond funds") — NEVER name tickers
3. account_optimization: which asset types belong in 401k vs Roth IRA vs taxable brokerage for tax efficiency
4. market_context: cite SPECIFIC data points from the live market data (e.g., "With the Fed funds rate at X%, bonds now offer meaningful yield") — not generic statements
5. rebalancing_guidance: what percentage drift triggers a rebalance and how often to review
6. risk_alignment: one sentence confirming how the allocation matches the user's risk tolerance and horizon

## CONTEXT
You receive live market data (S&P 500 price, YTD return, inflation rate, Fed funds rate, 10-year Treasury yield) and the investor's risk profile, horizon, and goals. If any data field shows "data unavailable", note it explicitly and adjust your confidence statement accordingly.

## HARD CONSTRAINTS — violations will cause your output to be blocked
- NEVER name a specific stock ticker (AAPL, MSFT, TSLA, etc.)
- NEVER name a specific ETF ticker (SPY, VTI, BND, QQQ, etc.) — describe the category only
- NEVER use: "guaranteed", "certain", "will definitely", "risk-free profit", "you will earn"
- NEVER recommend specific cryptocurrencies by name
- Allocations must sum to exactly 100% — check before outputting
- Always include: "Past performance does not guarantee future results" in risk_alignment

## Chain-of-thought required — think through each step:
Step 1: Assess risk profile (conservative/moderate/aggressive) and investment horizon
Step 2: Interpret current macro environment — what do the specific rate and inflation numbers mean for asset classes?
Step 3: Derive allocation percentages from risk + macro analysis
Step 4: Map allocation to account types for maximum tax efficiency
Step 5: Write market_context citing the actual numbers from the live data provided
Step 6: Verify allocations sum to 100, then return JSON

Respond only in valid JSON. Begin your response with: {"""


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
