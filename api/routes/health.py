import os
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str


class ReadinessResponse(BaseModel):
    status: str
    checks: dict


@router.get("/health", response_model=HealthResponse)
async def health():
    """Liveness check — returns 200 if the process is running."""
    return {"status": "ok", "version": "1.0.0"}


@router.get("/ready", response_model=ReadinessResponse)
async def ready():
    """
    Readiness check — verifies required environment variables are present.
    Used by cloud load balancers to determine if the instance can serve traffic.
    Does NOT make live API calls — just checks key presence.
    """
    checks = {
        "huggingface_api_key": bool(os.getenv("HUGGINGFACE_API_KEY")),
        "fred_api_key":        bool(os.getenv("FRED_API_KEY")),
        "langsmith_api_key":   bool(os.getenv("LANGSMITH_API_KEY")),
    }
    all_ready = all(checks.values())
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
    }
