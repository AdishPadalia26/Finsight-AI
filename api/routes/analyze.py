"""
/analyze endpoints

POST /analyze          — streams agent events as SSE, then final report
POST /analyze/sync     — blocking version, returns full result as JSON (for testing)
GET  /analyze/demo/{persona} — returns pre-loaded persona profile for the frontend
"""

import json
import uuid
import asyncio
from typing import Optional, Literal
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from graph.workflow import app as graph_app
from graph.state import FinancialProfile
from data.mock_profiles import PERSONAS
from api.middleware.audit_logger import log_request

router = APIRouter()

# ── Request / Response models ─────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """
    Two input modes:
    1. raw_input — free text from the form (Profile Builder agent extracts the data)
    2. profile   — pre-structured dict (used when loading a demo persona)
    Exactly one must be provided.
    """
    raw_input: Optional[str] = Field(None, description="Free-text financial description")
    profile:   Optional[dict] = Field(None, description="Pre-structured FinancialProfile dict")
    session_id: Optional[str] = Field(None, description="Optional session ID; generated if not provided")


class SyncAnalyzeResponse(BaseModel):
    session_id: str
    status: str
    final_report: Optional[dict]
    compliance_audit: Optional[dict]
    pipeline_errors: Optional[list]


# ── SSE helpers ───────────────────────────────────────────────────────────────

def _sse(data: dict) -> str:
    """Format a dict as a Server-Sent Event line."""
    return f"data: {json.dumps(data)}\n\n"


def _build_initial_state(request: AnalyzeRequest) -> dict:
    """Build the initial LangGraph state from the request."""
    session_id = request.session_id or str(uuid.uuid4())

    if request.profile:
        # Pre-structured profile (demo persona or frontend form)
        state = {**request.profile, "session_id": session_id, "revision_count": 0, "pipeline_errors": None}
    elif request.raw_input:
        # Free text — Profile Builder agent will extract the profile
        state = {
            "raw_input": request.raw_input,
            "session_id": session_id,
            "revision_count": 0,
            "pipeline_errors": None,
        }
    else:
        raise HTTPException(status_code=422, detail="Provide either raw_input or profile.")

    return state


# Agent display names shown in the frontend pipeline view
_AGENT_LABELS = {
    "profile_builder":       "Profile Builder",
    "behavioral_pattern":    "Behavioral Pattern Analyzer",
    "credit_intelligence":   "Credit Intelligence",
    "tier1_join":            None,   # internal sync node — don't surface to UI
    "tier2_entry":           None,
    "tier2_join":            None,
    "budget_architect":      "Budget Architect",
    "goal_engineering":      "Goal Engineering",
    "investment_strategist": "Investment Strategist",
    "tax_intelligence":      "Tax Intelligence",
    "debt_elimination":      "Debt Elimination",
    "life_event":            "Life Event Anticipation",
    "critic":                "Critic / Red Team",
    "compliance":            "Compliance Gate",
    "memory":                "Memory Agent",
}


# ── POST /analyze — SSE streaming ─────────────────────────────────────────────

@router.post("")
async def analyze_stream(request: AnalyzeRequest):
    """
    Runs the full 12-agent FinSight AI pipeline and streams each agent's
    completion event as a Server-Sent Event.

    SSE event types:
      pipeline_start   — pipeline has begun
      agent_start      — an agent node has started
      agent_complete   — an agent node has finished (includes partial output)
      revision_loop    — Critic triggered a revision back to Tier 2
      pipeline_complete — all agents done, full final_report included
      pipeline_error   — critical error (e.g. injection detected, compliance violation)
    """
    initial_state = _build_initial_state(request)
    session_id = initial_state["session_id"]
    log_request(session_id, "stream")

    async def event_stream():
        yield _sse({"event": "pipeline_start", "session_id": session_id,
                    "total_agents": 12, "built_agents": 6})
        try:
            async for event in graph_app.astream_events(initial_state, version="v2"):
                event_type = event.get("event", "")
                node_name  = event.get("name", "")
                label      = _AGENT_LABELS.get(node_name)

                # Skip internal sync nodes and non-node events
                if label is None:
                    continue

                if event_type == "on_chain_start":
                    yield _sse({
                        "event":  "agent_start",
                        "agent":  node_name,
                        "label":  label,
                        "status": "running",
                    })

                elif event_type == "on_chain_end":
                    output = event.get("data", {}).get("output", {})

                    # Detect revision loop (Tier 2 re-entry after Critic)
                    if node_name == "tier2_entry" and isinstance(output, dict):
                        revision = output.get("revision_count", 0)
                        if revision > 0:
                            yield _sse({
                                "event":          "revision_loop",
                                "revision_number": revision,
                                "message":        f"Critic requested revision #{revision} — re-running planning agents",
                            })
                        continue

                    # Surface safe summary fields only — never stream raw financial data
                    safe_output = _safe_output_summary(node_name, output)
                    yield _sse({
                        "event":  "agent_complete",
                        "agent":  node_name,
                        "label":  label,
                        "status": "complete",
                        "summary": safe_output,
                    })

                elif event_type == "on_chain_error":
                    error_msg = str(event.get("data", {}).get("error", "Unknown error"))
                    yield _sse({
                        "event":   "pipeline_error",
                        "agent":   node_name,
                        "message": error_msg[:300],  # truncate — never leak stack traces
                    })
                    return

            # Pipeline completed — stream the final report
            final_state = await graph_app.ainvoke(initial_state)
            yield _sse({
                "event":           "pipeline_complete",
                "session_id":      session_id,
                "final_report":    final_state.get("final_report"),
                "compliance_audit": final_state.get("compliance_audit"),
                "critic_scores":   final_state.get("critic_scores"),
                "pipeline_errors": final_state.get("pipeline_errors"),
            })

        except ValueError as e:
            # Injection detected or validation error
            yield _sse({"event": "pipeline_error", "message": str(e)[:200]})
        except Exception as e:
            yield _sse({"event": "pipeline_error", "message": f"Unexpected error: {str(e)[:200]}"})

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ── POST /analyze/sync — blocking (for testing + evaluation) ──────────────────

@router.post("/sync", response_model=SyncAnalyzeResponse)
async def analyze_sync(request: AnalyzeRequest):
    """
    Synchronous version — runs the full pipeline and returns the complete result.
    Use this for testing, evaluation, or when SSE is not supported.
    """
    initial_state = _build_initial_state(request)
    session_id = initial_state["session_id"]
    log_request(session_id, "sync")

    try:
        final_state = await asyncio.get_event_loop().run_in_executor(
            None, graph_app.invoke, initial_state
        )
        return SyncAnalyzeResponse(
            session_id=session_id,
            status="complete",
            final_report=final_state.get("final_report"),
            compliance_audit=final_state.get("compliance_audit"),
            pipeline_errors=final_state.get("pipeline_errors"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)[:300]}")


# ── GET /analyze/demo/{persona} — load a pre-built demo persona ───────────────

@router.get("/demo/{persona}")
async def get_demo_persona(persona: Literal["alex", "jordan", "sam"]):
    """
    Returns a pre-built demo persona profile ready to submit to /analyze.
    Used by the Streamlit frontend's "Load Demo" buttons.
    """
    profile = PERSONAS.get(persona)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Persona '{persona}' not found. Use: alex, jordan, sam")
    return {"persona": persona, "profile": profile}


# ── Safe output summary — never stream raw financial data ─────────────────────

def _safe_output_summary(node_name: str, output: dict) -> dict:
    """
    Returns a safe, non-sensitive summary of each agent's output for the SSE stream.
    Raw financial figures (income, debts, SSN equivalents) are never streamed —
    only scores, statuses, and non-sensitive summaries.
    """
    if not isinstance(output, dict):
        return {}

    summaries = {
        "profile_builder": lambda o: {
            "age": o.get("age"), "location": o.get("location"),
            "risk_tolerance": o.get("risk_tolerance"),
        },
        "behavioral_pattern": lambda o: {
            "discipline_score": (o.get("behavioral_fingerprint") or {}).get("discipline_score"),
            "key_insight": (o.get("behavioral_fingerprint") or {}).get("key_insight"),
        },
        "budget_architect": lambda o: {
            "health_score": (o.get("budget_recommendation") or {}).get("health_score", {}).get("total"),
            "grade":        (o.get("budget_recommendation") or {}).get("health_score", {}).get("grade"),
            "framework":    (o.get("budget_recommendation") or {}).get("recommended_framework"),
        },
        "investment_strategist": lambda o: {
            "allocation_summary": (o.get("investment_strategy") or {}).get("allocation"),
            "risk_alignment":     (o.get("investment_strategy") or {}).get("risk_alignment"),
        },
        "critic": lambda o: {
            "status":       (o.get("critic_scores") or {}).get("status"),
            "lowest_score": (o.get("critic_scores") or {}).get("lowest_score"),
            "average_score": (o.get("critic_scores") or {}).get("average_score"),
        },
        "compliance": lambda o: {
            "action":    (o.get("compliance_audit") or {}).get("action"),
            "audit_id":  (o.get("compliance_audit") or {}).get("audit_id"),
        },
    }

    fn = summaries.get(node_name)
    return fn(output) if fn else {"status": "complete"}
