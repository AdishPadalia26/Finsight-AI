"""
/analyze endpoints

POST /analyze          — streams agent events as SSE, then final report
POST /analyze/sync     — blocking version, returns full result as JSON (for testing)
GET  /analyze/demo/{persona} — returns pre-loaded demo persona profile for the frontend
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

GRAPH_CONFIG = {"recursion_limit": 100}

# ── Request / Response models ─────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
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
    return f"data: {json.dumps(data)}\n\n"


def _build_initial_state(request: AnalyzeRequest) -> dict:
    session_id = request.session_id or str(uuid.uuid4())
    if request.profile:
        state = {**request.profile, "session_id": session_id, "revision_count": 0, "pipeline_errors": []}
    elif request.raw_input:
        state = {
            "raw_input": request.raw_input,
            "session_id": session_id,
            "revision_count": 0,
            "pipeline_errors": [],
        }
    else:
        raise HTTPException(status_code=422, detail="Provide either raw_input or profile.")
    return state


_AGENT_LABELS = {
    "profile_builder":       "Profile Builder",
    "behavioral_pattern":    "Behavioral Pattern Analyzer",
    "credit_intelligence":   "Credit Intelligence",
    "tier1_join":            None,
    "tier2_entry":           None,
    "tier2_join":            None,
    "budget_architect":      "Budget Architect",
    "goal_engineering":      "Goal Engineering",
    "investment_strategist": "Investment Strategist",
    "tax_intelligence":      "Tax Intelligence",
    "debt_elimination":      "Debt Elimination",
    "life_event":            "Life Event Anticipation",
    "stress_test":           None,   # internal deterministic — don't surface separately
    "personalised_advisor":  "Personalised Advisor",
    "critic":                "Critic / Red Team",
    "compliance":            "Compliance Gate",
    "final_report_assembler": None,  # internal assembler
    "memory":                "Memory Agent",
}


# ── POST /analyze — SSE streaming ─────────────────────────────────────────────

@router.post("")
async def analyze_stream(request: AnalyzeRequest):
    """
    Runs the full FinSight AI pipeline and streams each agent's completion event
    as Server-Sent Events. The final state is captured from the stream itself —
    the pipeline runs exactly once.

    SSE event types:
      pipeline_start    — pipeline has begun
      agent_start       — an agent node has started
      agent_complete    — an agent node has finished (includes safe summary)
      revision_loop     — Critic triggered a revision back to Tier 2
      pipeline_complete — all agents done, canonical final_report included
      pipeline_error    — critical error (injection detected, compliance violation)
    """
    initial_state = _build_initial_state(request)
    session_id = initial_state["session_id"]
    log_request(session_id, "stream")

    # Heartbeat interval (seconds). Agent LLM calls can take minutes with no SSE
    # output; without periodic bytes, proxies (Cloudflare/Render, nginx) drop the
    # idle connection and the client sees the stream "close" mid-analysis.
    HEARTBEAT_SECONDS = 15
    _DONE = object()

    async def _run_pipeline(queue: "asyncio.Queue") -> None:
        """Drives the graph, pushing SSE frames onto the queue. Runs concurrently
        with the heartbeat loop in event_stream()."""
        # Accumulate state as each node completes — avoids double pipeline execution
        state_accumulator: dict = dict(initial_state)

        try:
            async for event in graph_app.astream_events(
                initial_state,
                config=GRAPH_CONFIG,
                version="v2",
            ):
                event_type = event.get("event", "")
                node_name  = event.get("name", "")
                label      = _AGENT_LABELS.get(node_name)

                if event_type == "on_chain_end":
                    output = event.get("data", {}).get("output", {})
                    if isinstance(output, dict):
                        # Merge delta into accumulated state (handle pipeline_errors reducer)
                        for k, v in output.items():
                            if k == "pipeline_errors" and isinstance(v, list):
                                existing = list(state_accumulator.get("pipeline_errors") or [])
                                state_accumulator["pipeline_errors"] = existing + v
                            else:
                                state_accumulator[k] = v

                    # Surface revision loop event
                    if node_name == "tier2_entry" and isinstance(output, dict):
                        revision = output.get("revision_count", 0)
                        if revision > 0:
                            await queue.put(_sse({
                                "event":           "revision_loop",
                                "revision_number":  revision,
                                "message":         f"Critic requested revision #{revision} — re-running planning agents",
                            }))
                        continue

                    if label is None:
                        continue

                    safe_output = _safe_output_summary(node_name, output)
                    await queue.put(_sse({
                        "event":   "agent_complete",
                        "agent":   node_name,
                        "label":   label,
                        "status":  "complete",
                        "summary": safe_output,
                    }))

                elif event_type == "on_chain_start":
                    if label is None:
                        continue
                    await queue.put(_sse({
                        "event":  "agent_start",
                        "agent":  node_name,
                        "label":  label,
                        "status": "running",
                    }))

                elif event_type == "on_chain_error":
                    error_msg = str(event.get("data", {}).get("error", "Unknown error"))
                    await queue.put(_sse({
                        "event":   "pipeline_error",
                        "agent":   node_name,
                        "message": error_msg[:300],
                    }))
                    return

            # Pipeline completed — emit final report from accumulated state
            await queue.put(_sse({
                "event":            "pipeline_complete",
                "session_id":       session_id,
                "final_report":     state_accumulator.get("final_report"),
                "compliance_audit": state_accumulator.get("compliance_audit"),
                "critic_scores":    state_accumulator.get("critic_scores"),
                "pipeline_errors":  state_accumulator.get("pipeline_errors") or [],
            }))

        except ValueError as e:
            await queue.put(_sse({"event": "pipeline_error", "message": str(e)[:200]}))
        except Exception as e:
            await queue.put(_sse({"event": "pipeline_error", "message": f"Unexpected error: {str(e)[:200]}"}))

    async def event_stream():
        yield _sse({
            "event": "pipeline_start",
            "session_id": session_id,
            "total_agents": 12,
            "built_agents": 12,
        })

        queue: asyncio.Queue = asyncio.Queue()
        producer = asyncio.create_task(_run_pipeline(queue))
        try:
            while True:
                try:
                    frame = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_SECONDS)
                except asyncio.TimeoutError:
                    # SSE comment line — ignored by EventSource/parsers, but the
                    # bytes keep the proxy connection alive during long agent runs.
                    yield ": keepalive\n\n"
                    continue
                yield frame
                # Stop once the pipeline signals completion or a fatal error.
                if '"event": "pipeline_complete"' in frame or '"event": "pipeline_error"' in frame:
                    break
        finally:
            producer.cancel()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── POST /analyze/sync ────────────────────────────────────────────────────────

@router.post("/sync", response_model=SyncAnalyzeResponse)
async def analyze_sync(request: AnalyzeRequest):
    """Synchronous version — runs full pipeline, returns complete result."""
    initial_state = _build_initial_state(request)
    session_id = initial_state["session_id"]
    log_request(session_id, "sync")

    try:
        loop = asyncio.get_running_loop()
        final_state = await loop.run_in_executor(
            None, lambda: graph_app.invoke(initial_state, config=GRAPH_CONFIG)
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


# ── GET /analyze/demo/{persona} ───────────────────────────────────────────────

@router.get("/demo/{persona}")
async def get_demo_persona(persona: Literal["alex", "jordan", "sam"]):
    """Returns a pre-built demo persona ready to submit to /analyze."""
    profile = PERSONAS.get(persona)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Persona '{persona}' not found.")
    return {"persona": persona, "profile": profile}


# ── Safe output summary ───────────────────────────────────────────────────────

def _safe_output_summary(node_name: str, output: dict) -> dict:
    """Returns a non-sensitive summary of each agent's output for SSE."""
    if not isinstance(output, dict):
        return {}

    summaries = {
        "profile_builder": lambda o: {
            "age": o.get("age"),
            "location": o.get("location"),
            "risk_tolerance": o.get("risk_tolerance"),
        },
        "behavioral_pattern": lambda o: {
            "discipline_score": (o.get("behavioral_fingerprint") or {}).get("discipline_score"),
            "key_insight": (o.get("behavioral_fingerprint") or {}).get("key_insight"),
        },
        "budget_architect": lambda o: {
            "health_score": (o.get("budget_recommendation") or {}).get("health_score", {}).get("total"),
            "grade": (o.get("budget_recommendation") or {}).get("health_score", {}).get("grade"),
            "framework": (o.get("budget_recommendation") or {}).get("recommended_framework"),
        },
        "goal_engineering": lambda o: {
            "goals_analyzed": len(((o.get("goal_roadmap") or {}).get("computed_goals")) or []),
            "funding_gap": ((o.get("goal_roadmap") or {}).get("cross_goal_summary") or {}).get("funding_gap"),
        },
        "investment_strategist": lambda o: {
            "allocation": (o.get("investment_strategy") or {}).get("allocation"),
            "risk_alignment": (o.get("investment_strategy") or {}).get("risk_alignment"),
        },
        "debt_elimination": lambda o: {
            "method": (o.get("debt_roadmap") or {}).get("recommended_method"),
            "total_debt": (o.get("debt_roadmap") or {}).get("total_debt_balance"),
        },
        "tax_intelligence": lambda o: {
            "savings_potential": (o.get("tax_opportunities") or {}).get("total_annual_savings_potential"),
        },
        "life_event": lambda o: {
            "events_detected": len(((o.get("life_events") or {}).get("events")) or []),
        },
        "personalised_advisor": lambda o: {
            "priority_count": len(((o.get("personalised_advice") or {}).get("priority_actions")) or []),
        },
        "critic": lambda o: {
            "status": (o.get("critic_scores") or {}).get("status"),
        },
        "compliance": lambda o: {
            "action": (o.get("compliance_audit") or {}).get("action"),
            "audit_id": (o.get("compliance_audit") or {}).get("audit_id"),
        },
    }

    fn = summaries.get(node_name)
    return fn(output) if fn else {"status": "complete"}
