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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routes.analyze import router as analyze_router
from api.routes.health import router as health_router

load_dotenv()

app = FastAPI(
    title="FinSight AI",
    description="Multi-agent financial intelligence platform — Wipro FDE Assignment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS — allow Streamlit frontend (localhost dev + Streamlit Cloud prod) ────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",      # Streamlit local dev
        "http://localhost:3000",      # Next.js if used
        "https://*.streamlit.app",   # Streamlit Cloud
        os.getenv("FRONTEND_URL", "*"),  # Cloud deployment override
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(analyze_router, prefix="/analyze", tags=["Analysis"])
app.include_router(health_router, tags=["Health"])
