"""
FinSight AI — FastAPI Backend Entry Point

Endpoints:
  POST /analyze          — streams agent events via Server-Sent Events (SSE)
  POST /analyze/sync     — synchronous version for testing
  GET  /analyze/demo/{persona}  — load a pre-built demo persona
  GET  /health           — liveness check
  GET  /ready            — readiness check (verifies HF + FRED keys present)
"""

import os
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Force UTF-8 stdout/stderr on Windows so agent prints (containing em-dashes,
# LLM unicode, etc.) don't crash the worker with UnicodeEncodeError under cp1252.
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from api.routes.analyze import router as analyze_router
from api.routes.health import router as health_router
from api.routes.report import router as report_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm the market data cache so the market bar shows data immediately."""
    async def _prefetch():
        await asyncio.sleep(3)  # Let the server fully start first
        loop = asyncio.get_running_loop()
        try:
            from tools.data.market_data import (
                get_sp500_price, get_inflation_rate,
                get_fed_funds_rate, get_10yr_treasury,
            )
            await asyncio.gather(
                loop.run_in_executor(None, get_sp500_price),
                loop.run_in_executor(None, get_inflation_rate),
                loop.run_in_executor(None, get_fed_funds_rate),
                loop.run_in_executor(None, get_10yr_treasury),
            )
        except Exception:
            pass

    asyncio.create_task(_prefetch())
    yield


app = FastAPI(
    lifespan=lifespan,
    title="FinSight AI",
    description="Multi-agent financial intelligence platform — Wipro FDE Assignment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS — allow local dev origins plus optional production override ─────────
_allowed_origins = [
    "http://localhost:8501",      # Streamlit local dev
    "http://localhost:3000",      # Next.js dev
    "http://127.0.0.1:3000",      # Next.js dev (loopback)
]
_frontend_url = os.getenv("FRONTEND_URL")
if _frontend_url and _frontend_url != "*":
    _allowed_origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=r"https://.*\.streamlit\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(analyze_router, prefix="/analyze", tags=["Analysis"])
app.include_router(health_router, tags=["Health"])
app.include_router(report_router, prefix="/report", tags=["Report"])
