"""
Instrumented pipeline test — tracks which provider (Gemini / Groq) each
agent actually used, and whether the call succeeded or fell back.
"""
import sys, io, time, threading
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv()

# ── Instrumentation setup (must happen before any agent imports) ───────────────

call_log: list[dict] = []
_current_agent = threading.local()   # thread-safe: parallel agents each get own slot
_lock = threading.Lock()

import agents.llm_client as llm_mod

_orig_gemini = llm_mod._call_gemini
_orig_nvidia  = llm_mod._call_nvidia
_orig_groq   = llm_mod._call_groq


def _patched_gemini(messages, temperature, max_tokens, preferred_model):
    result = _orig_gemini(messages, temperature, max_tokens, preferred_model)
    agent  = getattr(_current_agent, "name", "unknown")
    with _lock:
        call_log.append({
            "agent":    agent,
            "provider": "Gemini",
            "success":  result is not None,
            "chars":    len(result) if result else 0,
        })
    return result


def _patched_nvidia(messages, temperature, max_tokens, preferred_model):
    result = _orig_nvidia(messages, temperature, max_tokens, preferred_model)
    agent  = getattr(_current_agent, "name", "unknown")
    with _lock:
        call_log.append({
            "agent":    agent,
            "provider": "NVIDIA NIM",
            "success":  result is not None,
            "chars":    len(result) if result else 0,
        })
    return result


def _patched_groq(messages, temperature, max_tokens, preferred_model):
    result = _orig_groq(messages, temperature, max_tokens, preferred_model)
    agent  = getattr(_current_agent, "name", "unknown")
    with _lock:
        call_log.append({
            "agent":    agent,
            "provider": "Groq",
            "success":  True,
            "chars":    len(result) if result else 0,
        })
    return result


llm_mod._call_gemini = _patched_gemini
llm_mod._call_nvidia  = _patched_nvidia
llm_mod._call_groq   = _patched_groq

# Patch BaseAgent._call_llm to stamp current agent name before each LLM call
from graph.nodes import BaseAgent

_orig_call_llm = BaseAgent._call_llm

def _patched_call_llm(self, user_message: str) -> str:
    _current_agent.name = self.name
    return _orig_call_llm(self, user_message)

BaseAgent._call_llm = _patched_call_llm

# ── Run pipeline ───────────────────────────────────────────────────────────────

from data.mock_profiles import ALEX
from graph.workflow import app

print("=" * 64)
print("  FinSight AI — Per-Agent Gemini Coverage Test")
print("  Profile: ALEX (27, Austin TX, $5,500/mo income)")
print("=" * 64)
print()

start = time.time()

try:
    result = app.invoke(ALEX)
except Exception as exc:
    import traceback
    print(f"Pipeline crashed: {exc}")
    traceback.print_exc()
    sys.exit(1)

elapsed = time.time() - start

# ── Results table ──────────────────────────────────────────────────────────────

print(f"\nPipeline completed in {elapsed:.1f}s")
print()

if not call_log:
    print("WARNING: No LLM calls were recorded — check instrumentation.")
else:
    col = {"agent": 30, "provider": 16, "status": 8, "chars": 6}
    header = (
        f"{'Agent':<{col['agent']}}"
        f"{'Provider':<{col['provider']}}"
        f"{'OK':<{col['status']}}"
        f"{'Chars':>{col['chars']}}"
    )
    print(header)
    print("-" * sum(col.values()))
    for entry in call_log:
        ok = "YES" if entry["success"] else "MISS"
        print(
            f"{entry['agent']:<{col['agent']}}"
            f"{entry['provider']:<{col['provider']}}"
            f"{ok:<{col['status']}}"
            f"{entry['chars']:>{col['chars']}}"
        )

# ── Summary ────────────────────────────────────────────────────────────────────

gemini_ok   = [e for e in call_log if e["provider"] == "Gemini"     and e["success"]]
gemini_miss = [e for e in call_log if e["provider"] == "Gemini"     and not e["success"]]
nvidia_ok   = [e for e in call_log if e["provider"] == "NVIDIA NIM" and e["success"]]
nvidia_miss = [e for e in call_log if e["provider"] == "NVIDIA NIM" and not e["success"]]
groq_calls  = [e for e in call_log if e["provider"] == "Groq"       and e["success"]]

total = len(call_log)
print()
print("=" * 64)
print(f"  Total LLM calls : {total}")
print(f"  Gemini          : {len(gemini_ok)} answered / {len(gemini_miss)} quota-miss")
print(f"  NVIDIA NIM      : {len(nvidia_ok)} answered / {len(nvidia_miss)} failed")
print(f"  Groq            : {len(groq_calls)} answered")
print("=" * 64)

# ── Pipeline health ────────────────────────────────────────────────────────────

report   = result.get("final_report") or {}
overview = report.get("overview") or {}
errors   = result.get("pipeline_errors") or []

print()
print("Financial Overview (Alex)")
print(f"  Health Score : {overview.get('health_score')} ({overview.get('health_grade')})")
print(f"  Net Worth    : ${overview.get('net_worth', 0):>10,.0f}")
print(f"  Surplus/mo   : ${overview.get('monthly_surplus', 0):>10,.0f}")
print(f"  Emerg. fund  : {overview.get('emergency_fund_months', 0):.1f} months")
print()

sections = ["behavioral_fingerprint","budget","investment","goals",
            "debt","tax","life_events","stress_tests",
            "personalised_advice","critic","compliance"]
print("Report sections:")
for s in sections:
    val = report.get(s)
    tag = "OK  " if val else "MISS"
    print(f"  [{tag}] {s}")

if errors:
    print(f"\nPipeline errors ({len(errors)}):")
    for e in errors:
        print(f"  - {e[:120]}")
else:
    print("\nNo pipeline errors.")
