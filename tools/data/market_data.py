import time
import os
from typing import Optional
import httpx
import yfinance as yf
from dotenv import load_dotenv

load_dotenv()

_FRED_KEY = os.getenv("FRED_API_KEY", "")
_FRED_BASE = "https://api.stlouisfed.org/fred/series/observations"

_CACHE: dict = {}
_CACHE_TTL = 3600


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


# ── yfinance helpers ──────────────────────────────────────────────────────────

def _fetch_yf_price(ticker: str) -> Optional[float]:
    t = yf.Ticker(ticker)
    info = t.fast_info
    price = getattr(info, "last_price", None)
    return round(float(price), 2) if price else None


def _fetch_yf_ytd_return(ticker: str) -> Optional[float]:
    t = yf.Ticker(ticker)
    hist = t.history(period="ytd")
    if hist.empty or len(hist) < 2:
        return None
    start = hist["Close"].iloc[0]
    end = hist["Close"].iloc[-1]
    return round((end - start) / start * 100, 2)


# ── Equity markets ────────────────────────────────────────────────────────────

def get_sp500_price() -> Optional[float]:
    return _cached("sp500", lambda: _fetch_yf_price("SPY"))


def get_sp500_ytd_return() -> Optional[float]:
    return _cached("sp500_ytd", lambda: _fetch_yf_ytd_return("SPY"))


def get_intl_equity_ytd() -> Optional[float]:
    """International equity YTD return via VXUS (Total Intl Stock Market ETF)."""
    return _cached("intl_equity_ytd", lambda: _fetch_yf_ytd_return("VXUS"))


def get_gold_price() -> Optional[float]:
    """Gold price via GLD ETF proxy."""
    return _cached("gold_price", lambda: _fetch_yf_price("GLD"))


def get_gold_ytd_return() -> Optional[float]:
    """Gold YTD return via GLD proxy."""
    return _cached("gold_ytd", lambda: _fetch_yf_ytd_return("GLD"))


def get_reit_ytd() -> Optional[float]:
    """US REIT YTD return via VNQ (Vanguard Real Estate ETF)."""
    return _cached("reit_ytd", lambda: _fetch_yf_ytd_return("VNQ"))


def get_vix() -> Optional[float]:
    """CBOE Volatility Index — market fear gauge."""
    return _cached("vix", lambda: _fetch_yf_price("^VIX"))


# ── Fixed income ──────────────────────────────────────────────────────────────

def get_total_bond_price() -> Optional[float]:
    """US aggregate bond market via BND ETF."""
    return _cached("bnd", lambda: _fetch_yf_price("BND"))


# ── FRED API ──────────────────────────────────────────────────────────────────

def _fetch_fred_latest(series_id: str) -> Optional[float]:
    if not _FRED_KEY:
        return None
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


def _fetch_fred_cpi_yoy() -> Optional[float]:
    """Compute CPI YoY % from 14 months of CPIAUCSL — avoids the raw index value bug."""
    if not _FRED_KEY:
        return None
    params = {
        "series_id": "CPIAUCSL",
        "api_key": _FRED_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": 14,
    }
    with httpx.Client(timeout=10) as client:
        r = client.get(_FRED_BASE, params=params)
        r.raise_for_status()
        observations = r.json().get("observations", [])
    vals = [float(o["value"]) for o in observations if o.get("value", ".") != "."]
    if len(vals) < 13:
        return None
    return round((vals[0] - vals[12]) / vals[12] * 100, 2)


def get_inflation_rate() -> Optional[float]:
    """US CPI year-over-year inflation rate (%) — computed from FRED CPIAUCSL 13-month delta."""
    return _cached("inflation", _fetch_fred_cpi_yoy)


def get_fed_funds_rate() -> Optional[float]:
    """Federal Funds effective rate — FRED FEDFUNDS."""
    return _cached("fed_funds", lambda: _fetch_fred_latest("FEDFUNDS"))


def get_10yr_treasury() -> Optional[float]:
    """10-year US Treasury yield — FRED GS10."""
    return _cached("treasury_10yr", lambda: _fetch_fred_latest("GS10"))


def get_3mo_treasury() -> Optional[float]:
    """3-month Treasury bill yield — FRED TB3MS."""
    return _cached("treasury_3mo", lambda: _fetch_fred_latest("TB3MS"))


def get_corporate_bond_spread() -> Optional[float]:
    """BBB corporate bond option-adjusted spread — FRED BAMLC0A4CBBB."""
    return _cached("corp_spread", lambda: _fetch_fred_latest("BAMLC0A4CBBB"))


# ── Unified snapshots ─────────────────────────────────────────────────────────

def get_market_snapshot() -> dict:
    """Legacy snapshot — kept for backward compatibility with InvestmentStrategistAgent."""
    return {
        "sp500_price":        get_sp500_price(),
        "sp500_ytd_return":   get_sp500_ytd_return(),
        "bond_price":         get_total_bond_price(),
        "inflation_rate_pct": get_inflation_rate(),
        "fed_funds_rate_pct": get_fed_funds_rate(),
        "treasury_10yr_pct":  get_10yr_treasury(),
    }


def get_full_market_snapshot() -> dict:
    """Extended snapshot used by PersonalisedAdvisor and upgraded InvestmentStrategist."""
    return {
        # Equity
        "sp500_price":          get_sp500_price(),
        "sp500_ytd_return":     get_sp500_ytd_return(),
        "intl_equity_ytd":      get_intl_equity_ytd(),
        "reit_ytd":             get_reit_ytd(),
        # Safe haven
        "gold_price":           get_gold_price(),
        "gold_ytd_return":      get_gold_ytd_return(),
        # Fixed income
        "bond_price":           get_total_bond_price(),
        "treasury_10yr_pct":    get_10yr_treasury(),
        "treasury_3mo_pct":     get_3mo_treasury(),
        "corporate_spread_pct": get_corporate_bond_spread(),
        # Macro
        "inflation_rate_pct":   get_inflation_rate(),
        "fed_funds_rate_pct":   get_fed_funds_rate(),
        # Volatility
        "vix":                  get_vix(),
    }


def format_for_prompt(snapshot: dict) -> str:
    """Legacy format — used by InvestmentStrategistAgent."""
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


def format_full_snapshot_for_prompt(snapshot: dict) -> str:
    """Extended format injected into agent prompts."""
    def fmt(val, suffix="", prefix=""):
        return f"{prefix}{val}{suffix}" if val is not None else "unavailable"

    lines = [
        "=== LIVE MARKET DATA (free/open sources) ===",
        f"[EQUITY]",
        f"  S&P 500: {fmt(snapshot.get('sp500_price'), ' USD')}  |  YTD: {fmt(snapshot.get('sp500_ytd_return'), '%')}",
        f"  International Equity (VXUS) YTD: {fmt(snapshot.get('intl_equity_ytd'), '%')}",
        f"  US REITs (VNQ) YTD: {fmt(snapshot.get('reit_ytd'), '%')}",
        f"[SAFE HAVEN]",
        f"  Gold (GLD): {fmt(snapshot.get('gold_price'), ' USD/share')}  |  YTD: {fmt(snapshot.get('gold_ytd_return'), '%')}",
        f"[FIXED INCOME]",
        f"  US Agg Bond (BND): {fmt(snapshot.get('bond_price'), ' USD')}",
        f"  10-Yr Treasury: {fmt(snapshot.get('treasury_10yr_pct'), '%')}",
        f"  3-Mo T-Bill: {fmt(snapshot.get('treasury_3mo_pct'), '%')}",
        f"  BBB Corp Spread: {fmt(snapshot.get('corporate_spread_pct'), '%')}",
        f"[MACRO]",
        f"  CPI Inflation: {fmt(snapshot.get('inflation_rate_pct'), '%')}",
        f"  Fed Funds Rate: {fmt(snapshot.get('fed_funds_rate_pct'), '%')}",
        f"[VOLATILITY]",
        f"  VIX: {fmt(snapshot.get('vix'))}",
        "Note: 'unavailable' = data source unreachable — lower confidence in that asset class.",
    ]
    return "\n".join(lines)
