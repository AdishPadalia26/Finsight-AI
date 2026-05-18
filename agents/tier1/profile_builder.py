import json
import re
import uuid
from graph.nodes import BaseAgent
from tools.safety.pii_detector import redact_pii, detect_pii

_INJECTION_PATTERNS = [
    r"ignore\s+(previous|prior|all)\s+instructions",
    r"forget\s+your\s+instructions",
    r"you\s+are\s+now\s+a",
    r"new\s+persona",
    r"system\s*:",
    r"<\s*script",
    r"jailbreak",
    r"ignore\s+the\s+above",
    r"disregard\s+(all|previous)",
]
_INJECTION_RE = re.compile("|".join(_INJECTION_PATTERNS), re.IGNORECASE)

SYSTEM_PROMPT = """You are the Profile Builder Agent for FinSight AI, a financial intelligence platform.

Your ONLY job is to extract and structure financial information from user input into a valid JSON object.

STRICT OUTPUT RULES:
- Output ONLY a valid JSON object. No explanation, no preamble, no markdown.
- Start your response with { and end with }
- If a field is not mentioned, use null — do NOT invent or estimate values
- Normalize all currency values to USD floats (remove $, commas)
- age must be an integer between 18 and 100
- risk_tolerance must be exactly one of: "conservative", "moderate", "aggressive"
- monthly_income and monthly_expenses must be positive floats
- debts is a list of objects with keys: type, balance, interest_rate, minimum_payment
- goals is a list of objects with keys: description, target_amount, timeline_months, priority
- priority must be one of: "critical", "high", "medium", "low"

Required JSON structure:
{
  "age": <int>,
  "location": <string>,
  "monthly_income": <float>,
  "monthly_expenses": <float>,
  "savings": <float>,
  "investments": <float>,
  "property_value": <float>,
  "debts": [...],
  "goals": [...],
  "risk_tolerance": <string>,
  "investment_horizon": <int>
}"""


class ProfileBuilderAgent(BaseAgent):
    """
    Agent 01 — Profile Builder (Tier 1, Sequential)

    Sequential entry point. Runs BEFORE any LLM call:
    1. Injection detection — rejects malicious input
    2. PII detection and redaction
    3. Schema extraction via LLM
    4. Output validation

    Model: Mixtral-8x7B — fast, reliable structured JSON extraction.
    """

    MODEL_TYPE = "extraction"

    def __init__(self):
        super().__init__(name="ProfileBuilderAgent", system_prompt=SYSTEM_PROMPT)

    def run(self, state: dict) -> dict:
        raw_input = state.get("raw_input", "")

        # ── Step 1: Injection detection (before any LLM call) ──────────────
        if _INJECTION_RE.search(raw_input):
            raise ValueError("INJECTION_DETECTED: malicious input pattern found")

        # ── Step 2: PII detection + redaction ──────────────────────────────
        pii_found = detect_pii(raw_input)
        sanitized = redact_pii(raw_input)

        # ── Step 3: LLM extraction ──────────────────────────────────────────
        extracted = self._call_llm_json(
            f"Extract the financial profile from this user input:\n\n{sanitized}"
        )

        # ── Step 4: Validate required fields ───────────────────────────────
        self._validate(extracted)

        return {
            **state,
            "age":                int(extracted["age"]),
            "location":           str(extracted.get("location") or ""),
            "monthly_income":     float(extracted["monthly_income"]),
            "monthly_expenses":   float(extracted["monthly_expenses"]),
            "savings":            float(extracted.get("savings") or 0),
            "investments":        float(extracted.get("investments") or 0),
            "property_value":     float(extracted.get("property_value") or 0),
            "debts":              extracted.get("debts") or [],
            "goals":              extracted.get("goals") or [],
            "risk_tolerance":     extracted.get("risk_tolerance", "moderate"),
            "investment_horizon": int(extracted.get("investment_horizon") or 30),
            "session_id":         state.get("session_id") or str(uuid.uuid4()),
            "revision_count":     0,
            "pipeline_errors":    None,
            "_pii_detected":      pii_found,  # internal flag, never logged
        }

    def _validate(self, data: dict):
        required = ["age", "monthly_income", "monthly_expenses"]
        missing = [f for f in required if data.get(f) is None]
        if missing:
            raise ValueError(f"ProfileBuilder: missing required fields: {missing}")
        if not (18 <= int(data["age"]) <= 100):
            raise ValueError(f"ProfileBuilder: age {data['age']} out of valid range 18-100")
        if float(data["monthly_income"]) <= 0:
            raise ValueError("ProfileBuilder: monthly_income must be positive")
        if data.get("risk_tolerance") not in ("conservative", "moderate", "aggressive", None):
            data["risk_tolerance"] = "moderate"
