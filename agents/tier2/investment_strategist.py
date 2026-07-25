import json
from graph.nodes import BaseAgent
from tools.data import market_data
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
    PROVIDER = "openrouter"
    MODEL_ID = "openai/gpt-oss-120b:free"
    API_KEY_VAR = "OPENROUTER_API_KEY_2"
    FALLBACK_PROVIDER = "nvidia"
    FALLBACK_MODEL_ID = "moonshotai/kimi-k2.6"
    FALLBACK_API_KEY_VAR = "NVIDIA_API_KEY_1"

    def __init__(self):
        super().__init__(name="InvestmentStrategistAgent", system_prompt=SYSTEM_PROMPT)

    def run(self, state: dict) -> dict:
        # Pull extended live market data — handles None gracefully
        try:
            snapshot = market_data.get_full_market_snapshot()
        except Exception as e:
            print(f"[InvestmentStrategist] Market data unavailable - using fallback: {e}")
            snapshot = self._empty_market_snapshot()
        market_text = market_data.format_full_snapshot_for_prompt(snapshot)

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

        try:
            raw_result = self._call_llm_json(json.dumps(prompt_data))
        except (RuntimeError, ValueError) as e:
            print(f"[InvestmentStrategist] LLM unavailable — using fallback: {e}")
            raw_result = {
                "allocation": self._fallback_allocation(state.get("risk_tolerance")),
                "risk_alignment": (
                    f"Fallback allocation reflects a {state.get('risk_tolerance', 'moderate')} profile and "
                    "available investment horizon. Past performance does not guarantee future results."
                ),
                "recommendations": ["LLM analysis unavailable — default allocation shown."],
            }

        raw_result = self._normalize_result(raw_result, state)

        # Defense-in-depth: scan this agent's output before it leaves
        text_to_scan = json.dumps(raw_result)
        scan = scan_output(text_to_scan)
        if scan["severity"] == "CRITICAL":
            raise ValueError(
                f"InvestmentStrategist produced CRITICAL compliance violation: "
                f"{scan['violations']}"
            )

        # Inject raw market snapshot for frontend display
        raw_result["live_market_snapshot"] = snapshot
        raw_result["market_context"] = {
            k: v for k, v in snapshot.items() if v is not None
        }

        return {**state, "investment_strategy": raw_result}

    @classmethod
    def _normalize_result(cls, result: object, state: dict) -> dict:
        if not isinstance(result, dict):
            return cls._fallback_result(state, "Investment model returned a non-object response.")

        nested = result.get("investment_strategy")
        if isinstance(nested, dict):
            result = {**nested, **{k: v for k, v in result.items() if k != "investment_strategy"}}

        allocation = result.get("allocation")
        if isinstance(allocation, list):
            converted = {}
            for item in allocation:
                if not isinstance(item, dict):
                    continue
                name = item.get("asset_class") or item.get("name") or item.get("category")
                value = item.get("percentage") or item.get("value") or item.get("allocation")
                if isinstance(name, str) and isinstance(value, (int, float)):
                    converted[name.lower().replace(" ", "_")] = value
            allocation = converted

        if not isinstance(allocation, dict) or not allocation:
            return cls._fallback_result(state, "Investment model response did not include a usable allocation.")

        normalized_allocation = {
            str(k): float(v)
            for k, v in allocation.items()
            if isinstance(v, (int, float)) and v > 0
        }
        if not normalized_allocation:
            return cls._fallback_result(state, "Investment allocation did not include positive numeric weights.")

        total = sum(normalized_allocation.values())
        if total <= 0:
            return cls._fallback_result(state, "Investment allocation total was zero.")

        if abs(total - 100) > 0.01:
            normalized_allocation = {
                k: round(v / total * 100, 1)
                for k, v in normalized_allocation.items()
            }

        result["allocation"] = normalized_allocation
        result.setdefault(
            "risk_alignment",
            (
                f"Allocation reflects a {state.get('risk_tolerance', 'moderate')} profile and "
                "available investment horizon. Past performance does not guarantee future results."
            ),
        )
        result.setdefault("rationale", "Allocation generated by the investment strategist.")
        result["account_optimization"] = (
            result.get("account_optimization")
            if isinstance(result.get("account_optimization"), str) and result.get("account_optimization")
            else "Use tax-advantaged retirement accounts for higher-growth and income-producing assets when available; keep cash needs liquid and taxable holdings tax-efficient."
        )
        result["rationale"] = (
            result.get("rationale")
            if isinstance(result.get("rationale"), str) and result.get("rationale")
            else json.dumps(result.get("rationale")) if result.get("rationale") else "Allocation generated by the investment strategist."
        )
        result["risk_alignment"] = (
            result.get("risk_alignment")
            if isinstance(result.get("risk_alignment"), str) and result.get("risk_alignment")
            else json.dumps(result.get("risk_alignment")) if result.get("risk_alignment") else f"Allocation reflects a {state.get('risk_tolerance', 'moderate')} profile and available investment horizon. Past performance does not guarantee future results."
        )
        result.setdefault("rebalancing_guidance", "Review quarterly and rebalance when any asset class drifts more than 5 percentage points.")
        return result

    @classmethod
    def _fallback_result(cls, state: dict, reason: str) -> dict:
        return {
            "allocation": cls._fallback_allocation(state.get("risk_tolerance")),
            "risk_alignment": (
                f"Fallback allocation reflects a {state.get('risk_tolerance', 'moderate')} profile and "
                "available investment horizon. Past performance does not guarantee future results."
            ),
            "etf_categories": {
                "us_equities": "broad US equity index funds",
                "international_equities": "broad international equity index funds",
                "bonds": "investment-grade bond funds",
                "cash": "high-liquidity cash equivalents",
                "alternatives": "diversifying real-asset or alternative strategy funds",
            },
            "account_optimization": (
                "Use tax-advantaged retirement accounts for higher-growth and income-producing assets "
                "when available; keep cash needs liquid and taxable holdings tax-efficient."
            ),
            "rebalancing_guidance": "Review quarterly and rebalance when any asset class drifts more than 5 percentage points.",
            "rationale": reason,
            "fallback": True,
        }

    @staticmethod
    def _empty_market_snapshot() -> dict:
        return {
            "sp500_price": None,
            "sp500_ytd_return": None,
            "intl_equity_ytd": None,
            "reit_ytd": None,
            "gold_price": None,
            "gold_ytd_return": None,
            "bond_price": None,
            "treasury_10yr_pct": None,
            "treasury_3mo_pct": None,
            "corporate_spread_pct": None,
            "inflation_rate_pct": None,
            "fed_funds_rate_pct": None,
            "vix": None,
        }

    @staticmethod
    def _fallback_allocation(risk_tolerance: str | None) -> dict:
        if risk_tolerance == "conservative":
            return {
                "us_equities": 35,
                "international_equities": 15,
                "bonds": 35,
                "cash": 10,
                "alternatives": 5,
            }
        if risk_tolerance == "aggressive":
            return {
                "us_equities": 60,
                "international_equities": 25,
                "bonds": 10,
                "cash": 2,
                "alternatives": 3,
            }
        return {
            "us_equities": 50,
            "international_equities": 20,
            "bonds": 20,
            "cash": 5,
            "alternatives": 5,
        }
