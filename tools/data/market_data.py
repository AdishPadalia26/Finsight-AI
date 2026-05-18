import time
import os
from typing import Optional
import httpx
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

_FRED_KEY = os.getenv("FRED_API_KEY", "")
_FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

# Cache: {key: (value, fetched_at_unix_timestamp)}
_CACHE: dict = {}
_CACHE_TTL = 3600  # 1 hour


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


# ── yfinance (no API key, no rate limit, cloud-safe) ─────────────────────────

def _fetch_yf_price(ticker: str) -> Optional[float]:
    t = yf.Ticker(ticker)
    info = t.fast_info
    price = getattr(info, "last_price", None)
    return round(float(price), 2) if price else None


def get_sp500_price() -> Optional[float]:
    """Current S&P 500 level via SPY ETF — yfinance, no API key."""
    return _cached("sp500", lambda: _fetch_yf_price("SPY"))


def get_total_bond_price() -> Optional[float]:
    """Current US aggregate bond market level via BND ETF — yfinance, no API key."""
    return _cached("bnd", lambda: _fetch_yf_price("BND"))


def get_sp500_ytd_return() -> Optional[float]:
    """S&P 500 YTD return percentage."""
    def fetch():
        t = yf.Ticker("SPY")
        hist = t.history(period="ytd")
        if hist.empty or len(hist) < 2:
            return None
        start = hist["Close"].iloc[0]
        end = hist["Close"].iloc[-1]
        return round((end - start) / start * 100, 2)
    return _cached("sp500_ytd", fetch)


# ── FRED API (free, unlimited, official Federal Reserve data) ─────────────────

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
    """Latest US CPI year-over-year inflation rate (%) — FRED CPIAUCSL."""
    return _cached("inflation", lambda: _fetch_fred_latest("CPIAUCSL"))


def get_fed_funds_rate() -> Optional[float]:
    """Latest Federal Funds effective rate (%) — FRED FEDFUNDS."""
    return _cached("fed_funds", lambda: _fetch_fred_latest("FEDFUNDS"))


def get_10yr_treasury() -> Optional[float]:
    """Latest 10-year US Treasury yield (%) — FRED GS10."""
    return _cached("treasury_10yr", lambda: _fetch_fred_latest("GS10"))


# ── Unified snapshot ──────────────────────────────────────────────────────────

def get_market_snapshot() -> dict:
    """
    Fetches all market indicators. Returns None for any value that fails —
    agents must handle None gracefully and note 'data unavailable' in output.
    """
    return {
        "sp500_price":        get_sp500_price(),
        "sp500_ytd_return":   get_sp500_ytd_return(),
        "bond_price":         get_total_bond_price(),
        "inflation_rate_pct": get_inflation_rate(),
        "fed_funds_rate_pct": get_fed_funds_rate(),
        "treasury_10yr_pct":  get_10yr_treasury(),
    }


def format_for_prompt(snapshot: dict) -> str:
    """Format market snapshot as a clean string for injection into LLM prompts."""
    def fmt(val, suffix=""):
        return f"{val}{suffix}" if val is not None else "data unavailable"

    return (
        f"Current Market Conditions (live data):\n"
        f"- S&P 500 (SPY): {fmt(snapshot.get('sp500_price'), ' USD')}\n"
        f"- S&P 500 YTD Return: {fmt(snapshot.get('sp500_ytd_return'), '%')}\n"
        f"- US Aggregate Bonds (BND): {fmt(snapshot.get('bond_price'), ' USD')}\n"
        f"- Inflation Rate (CPI): {fmt(snapshot.get('inflation_rate_pct'), '%')}\n"
        f"- Federal Funds Rate: {fmt(snapshot.get('fed_funds_rate_pct'), '%')}\n"
        f"- 10-Year Treasury Yield: {fmt(snapshot.get('treasury_10yr_pct'), '%')}"
    )
