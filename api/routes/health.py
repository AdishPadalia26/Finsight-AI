import os
import time
import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class ReadinessResponse(BaseModel):
    status: str
    checks: dict


@router.get("/health")
async def health():
    """
    Liveness check. Returns cached market data immediately (non-blocking).
    Cache is populated on startup and refreshed when the pipeline runs.
    """
    # Import cache-read helpers — zero network I/O if cache is warm
    from tools.data.market_data import _CACHE

    def _cached_val(key: str) -> Optional[float]:
        entry = _CACHE.get(key)
        if entry:
            value, fetched_at = entry
            if time.time() - fetched_at < 3600:
                return value
        return None

    market_context = {
        "sp500_price":    _cached_val("sp500"),
        "inflation_rate": _cached_val("inflation"),
        "fed_funds_rate": _cached_val("fed_funds"),
        "treasury_10yr":  _cached_val("treasury_10yr"),
        "data_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    return {
        "status": "ok",
        "version": "1.0.0",
        "market_context": market_context,
    }


@router.get("/ready", response_model=ReadinessResponse)
async def ready():
    """
    Readiness check — verifies required environment variables are present.
    Does NOT make live API calls — just checks key presence.
    """
    checks = {
        "groq_api_key":        bool(os.getenv("GROQ_API_KEY")),
        "huggingface_api_key": bool(os.getenv("HUGGINGFACE_API_KEY")),
        "fred_api_key":        bool(os.getenv("FRED_API_KEY")),
        "langsmith_api_key":   bool(os.getenv("LANGSMITH_API_KEY")),
    }
    all_ready = all(checks.values())
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
    }
