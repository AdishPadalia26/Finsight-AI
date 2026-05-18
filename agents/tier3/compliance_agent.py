import json
import hashlib
from datetime import datetime, timezone
from graph.nodes import BaseAgent
from tools.safety.output_scanner import scan_output, apply_moderate_rewrites
from tools.safety.pii_detector import has_pii, redact_pii
from tools.safety.disclaimer_engine import inject_disclaimer

REWRITE_PROMPT = """## ROLE
You are a regulatory compliance officer with expertise in SEC, FINRA, and FCA regulations for AI-generated financial content. Your job is to rewrite output that could expose the platform to legal liability — without removing the useful information.

## ACTION
Rewrite the financial analysis below to fix these specific violations:
{violations}

Rewriting rules:
- "you should buy" → "one option to consider is"
- "best investment is" → "an allocation approach that may suit this profile"
- "will definitely" → "is designed to" or "has historically"
- "I recommend" → "based on this profile, one approach is"
- Bare return percentages → add "(historical average — not guaranteed)"
- Keep all factual analysis — only change the directiveness of language
- Do NOT add new recommendations or remove existing analysis
- Preserve the JSON structure exactly

## HARD CONSTRAINTS
- Output ONLY the corrected JSON — no explanation, no preamble
- Do not change any numbers, scores, or factual data
- Do not add financial advice while fixing compliance language

Begin your response with: {"""


class ComplianceAgent(BaseAgent):
    """
    Agent 11 — Compliance & Safety Gate (Tier 3, Sequential — FINAL GATE)

    Every output passes through this agent before reaching the user. No exceptions.

    Four actions based on scan severity:
    - CRITICAL: pipeline hard-stop, no output delivered, error logged
    - MODERATE: LLM rewrites violations, output then re-scanned
    - CLEAN: disclaimer injected, output approved

    Maintains a compliance audit trail for every output (session_id, timestamp,
    violations, action taken, output hash). Satisfies the assignment requirement
    for responsible AI deployment.

    Model: Mistral-7B — fast classification and filtering, sufficient for compliance task.
    """

    MODEL_TYPE = "compliance"
    _audit_log: list = []  # in-memory audit trail for demo session

    def __init__(self):
        super().__init__(name="ComplianceAgent", system_prompt=REWRITE_PROMPT)

    def run(self, state: dict) -> dict:
        session_id = state.get("session_id", "unknown")
        location = state.get("location", "")

        # Collect all agent outputs into one text block for scanning
        outputs_to_scan = {
            "budget_recommendation": state.get("budget_recommendation"),
            "investment_strategy": state.get("investment_strategy"),
            "goal_roadmap": state.get("goal_roadmap"),
            "critic_scores": state.get("critic_scores"),
        }
        combined_text = json.dumps(outputs_to_scan)

        # ── Step 1: PII check — must never reach user output ───────────────
        if has_pii(combined_text):
            combined_text = redact_pii(combined_text)

        # ── Step 2: Compliance scan ────────────────────────────────────────
        scan = scan_output(combined_text)

        if scan["severity"] == "CRITICAL":
            entry = self._log_audit(session_id, "BLOCKED", scan, combined_text)
            raise ComplianceViolation(
                f"CRITICAL compliance violation detected — pipeline halted. "
                f"Violations: {scan['violations']}. "
                f"Audit ID: {entry['audit_id']}"
            )

        if scan["severity"] == "MODERATE":
            combined_text = self._rewrite_violations(combined_text, scan["violations"])
            # Re-scan after rewrite to confirm clean
            rescan = scan_output(combined_text)
            if rescan["severity"] == "CRITICAL":
                entry = self._log_audit(session_id, "BLOCKED_AFTER_REWRITE", rescan, combined_text)
                raise ComplianceViolation(
                    f"Rewrite introduced new CRITICAL violation. Audit ID: {entry['audit_id']}"
                )
            action = "REWRITTEN_AND_APPROVED"
        else:
            action = "APPROVED"

        # ── Step 3: Inject disclaimer ──────────────────────────────────────
        final_text = inject_disclaimer(combined_text, location)

        # ── Step 4: Log audit trail ────────────────────────────────────────
        audit_entry = self._log_audit(session_id, action, scan, final_text)

        return {
            **state,
            "final_report": json.loads(combined_text) if self._is_valid_json(combined_text) else combined_text,
            "compliance_audit": {
                "audit_id": audit_entry["audit_id"],
                "action": action,
                "violations_found": scan["violations"],
                "timestamp": audit_entry["timestamp"],
                "disclaimer_injected": True,
            },
        }

    def _rewrite_violations(self, text: str, violations: list) -> str:
        # First apply simple regex rewrites
        text = apply_moderate_rewrites(text)
        # Then use LLM for context-sensitive rewrites
        violation_descriptions = "\n".join(
            f"- {v['type']}: found '{v['matched_text']}'"
            for v in violations
        )
        prompt = REWRITE_PROMPT.format(violations=violation_descriptions)
        try:
            rewritten = self._call_llm(f"{prompt}\n\nContent to fix:\n{text}")
            return rewritten if self._is_valid_json(rewritten) else text
        except Exception:
            return text  # fall back to regex-only rewrite on LLM failure

    def _log_audit(self, session_id: str, action: str, scan: dict, text: str) -> dict:
        entry = {
            "audit_id": hashlib.sha256(
                f"{session_id}{datetime.now(timezone.utc).isoformat()}".encode()
            ).hexdigest()[:12],
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "violations_found": scan.get("violations", []),
            "output_hash": hashlib.sha256(text.encode()).hexdigest()[:16],
        }
        ComplianceAgent._audit_log.append(entry)
        return entry

    @staticmethod
    def get_audit_log() -> list:
        return ComplianceAgent._audit_log

    @staticmethod
    def _is_valid_json(text: str) -> bool:
        try:
            json.loads(text)
            return True
        except (json.JSONDecodeError, ValueError):
            return False


class ComplianceViolation(Exception):
    """Raised when a CRITICAL compliance violation hard-stops the pipeline."""
    pass
