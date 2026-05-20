"""
Quick end-to-end test: verify Gemini API key works, then run the full
FinSight AI pipeline with the ALEX demo persona and print a summary.
"""
import os, sys, json, time, io
from dotenv import load_dotenv
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

load_dotenv()

# ── 1. Direct Gemini ping ──────────────────────────────────────────────────────
print("=" * 60)
print("STEP 1 — Direct Gemini API ping")
print("=" * 60)

from google import genai

key = os.getenv("GEMINI_API_KEY")
if not key:
    print("ERROR: GEMINI_API_KEY not set")
    sys.exit(1)

client = genai.Client(api_key=key)
try:
    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Reply with exactly: GEMINI_OK",
    )
    print(f"  Response: {resp.text.strip()}")
    print("  ✓ Gemini API key is valid and reachable\n")
except Exception as e:
    print(f"  ✗ Gemini ping failed: {e}")
    sys.exit(1)

# ── 2. Full pipeline with Alex persona ────────────────────────────────────────
print("=" * 60)
print("STEP 2 — Full pipeline with ALEX persona")
print("=" * 60)

from data.mock_profiles import ALEX
from graph.workflow import app

start = time.time()
print(f"  Age: {ALEX['age']} | Income: ${ALEX['monthly_income']:,.0f}/mo | "
      f"Savings: ${ALEX['savings']:,.0f}")
print(f"  Debts: {len(ALEX['debts'])} | Goals: {len(ALEX['goals'])}")
print("  Running pipeline...\n")

try:
    result = app.invoke(ALEX)
    elapsed = time.time() - start

    report = result.get("final_report") or {}
    overview = report.get("overview") or {}
    errors = result.get("pipeline_errors") or []

    print(f"  Pipeline completed in {elapsed:.1f}s")
    print(f"  Errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"    - {e[:120]}")

    print("\n── Financial Overview ──────────────────────────────────")
    print(f"  Health Score  : {overview.get('health_score')} ({overview.get('health_grade')})")
    print(f"  Net Worth     : ${overview.get('net_worth', 0):,.0f}")
    print(f"  Monthly Surplus: ${overview.get('monthly_surplus', 0):,.0f}")
    print(f"  Savings Rate  : {overview.get('savings_rate', 0):.1%}")
    print(f"  Debt-to-Income: {overview.get('debt_to_income', 0):.1%}")
    print(f"  Emergency Fund: {overview.get('emergency_fund_months', 0):.1f} months")

    # Show which LLM sections populated
    sections = ["behavioral_fingerprint", "budget", "investment", "goals",
                "debt", "tax", "life_events", "stress_tests",
                "personalised_advice", "critic", "compliance"]
    print("\n── Report Sections ─────────────────────────────────────")
    for sec in sections:
        val = report.get(sec)
        status = "✓" if val else "✗ (empty)"
        # show a snippet for LLM-generated sections
        snippet = ""
        if val and isinstance(val, dict):
            for k in ("summary", "narrative", "rationale", "recommendation", "advice_narrative"):
                if val.get(k):
                    snippet = f" | {str(val[k])[:80]}..."
                    break
        print(f"  [{status}] {sec}{snippet}")

    print("\n── Personalised Advice (first 300 chars) ───────────────")
    adv = report.get("personalised_advice") or {}
    narrative = adv.get("advice_narrative") or adv.get("summary") or str(adv)[:300]
    print(f"  {str(narrative)[:300]}")

    print("\n── Compliance ──────────────────────────────────────────")
    comp = report.get("compliance") or {}
    print(f"  Status   : {comp.get('status', 'N/A')}")
    print(f"  Disclaimer: {str(comp.get('disclaimer', ''))[:120]}")

except Exception as exc:
    import traceback
    print(f"\n✗ Pipeline failed: {exc}")
    traceback.print_exc()
    sys.exit(1)

print("\n✓ Test complete")
