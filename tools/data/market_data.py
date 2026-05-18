import os
import time
from typing import Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

_ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
_FRED_KEY = os.getenv("FRED_API_KEY", "")

_AV_BASE = "https://www.alphavantage.co/query"
_FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

# Cache: {cache_key: (value, fetched_at_timestamp)}
_CACHE: dict = {}
_CACHE_TTL = 3600  # 1 hour — Alpha Vantage free tier: 5 calls/min


def _cached(key: str, fetch_fn) -> Optional[float]:
    now = time.time()
    if key in _CACHE:
        value, fetched_at = _CACHE[key]
        if now - fetched_at < _CACHE_TTL:
            return value
    try:
        value = fetch_fn()
        if value is not None:
            _CACHE[key] = (value, now)
        return value
    except Exception:
        return None


# ── Alpha Vantage ─────────────────────────────────────────────────────────────

def _fetch_av_quote(symbol: str) -> Optional[float]:
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": _ALPHA_VANTAGE_KEY,
    }
    with httpx.Client(timeout=10) as client:
        r = client.get(_AV_BASE, params=params)
        r.raise_for_status()
        data = r.json()
        price_str = data.get("Global Quote", {}).get("05. price")
        return float(price_str) if price_str else None


def get_sp500_price() -> Optional[float]:
    """Current S&P 500 level via SPY ETF price."""
    return _cached("sp500", lambda: _fetch_av_quote("SPY"))


def get_total_bond_price() -> Optional[float]:
    """Current US aggregate bond market level via BND ETF price."""
    return _cached("bnd", lambda: _fetch_av_quote("BND"))


# ── FRED (Federal Reserve Economic Data) ─────────────────────────────────────

def _fetch_fred_latest(series_id: str) -> Optional[float]:
    params = {
        "series_id": series_id,
        "api_key": _FRED_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 1,
    }
    with httpx.Client(timeout=10) as client:
        r = client.get(_FRED_BASE, params=params)
        r.raise_for_status()
        observations = r.json().get("observations", [])
        if observations:
            val = observations[0].get("value", ".")
            return float(val) if val != "." else None
        return None


def get_inflation_rate() -> Optional[float]:
    """Latest US CPI year-over-year inflation rate (%)."""
    return _cached("inflation", lambda: _fetch_fred_latest("CPIAUCSL"))


def get_fed_funds_rate() -> Optional[float]:
    """Latest Federal Funds effective rate (%)."""
    return _cached("fed_funds", lambda: _fetch_fred_latest("FEDFUNDS"))


def get_10yr_treasury() -> Optional[float]:
    """Latest 10-year US Treasury yield (%)."""
    return _cached("treasury_10yr", lambda: _fetch_fred_latest("GS10"))


# ── Unified snapshot ─────────────────────────────────────────────────────────

def get_market_snapshot() -> dict:
    """
    Fetch all market indicators in one call.
    All values return None gracefully on API failure —
    callers must handle None before passing to LLM prompts.
    """
    return {
        "sp500_price": get_sp500_price(),
        "bond_price": get_total_bond_price(),
        "inflation_rate_pct": get_inflation_rate(),
        "fed_funds_rate_pct": get_fed_funds_rate(),
        "treasury_10yr_pct": get_10yr_treasury(),
    }


def format_for_prompt(snapshot: dict) -> str:
    """Format market snapshot as readable string for LLM system prompts."""
    def fmt(val, suffix=""):
        return f"{val}{suffix}" if val is not None else "data unavailable"

    return (
        f"Current Market Conditions (live data):\n"
        f"- S&P 500 (SPY): {fmt(snapshot.get('sp500_price'), '')}\n"
        f"- US Bonds (BND): {fmt(snapshot.get('bond_price'), '')}\n"
        f"- Inflation Rate (CPI): {fmt(snapshot.get('inflation_rate_pct'), '%')}\n"
        f"- Federal Funds Rate: {fmt(snapshot.get('fed_funds_rate_pct'), '%')}\n"
        f"- 10-Year Treasury Yield: {fmt(snapshot.get('treasury_10yr_pct'), '%')}"
    )
