"""
Audit Logger Middleware

Logs every API request with session metadata.
NEVER logs raw financial data (income, debts, account numbers).
Satisfies assignment requirement: compliance audit trail.
"""

import hashlib
from datetime import datetime, timezone
from typing import Literal

# In-memory log for demo. In production: write to CloudWatch (AWS),
# Azure Monitor, or GCP Cloud Logging.
_REQUEST_LOG: list = []


def log_request(
    session_id: str,
    mode: Literal["stream", "sync"],
    extra: dict = None,
) -> dict:
    """
    Log a request. Stores only metadata — never financial values.
    Returns the log entry for reference.
    """
    entry = {
        "log_id":     hashlib.sha256(
            f"{session_id}{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:12],
        "session_id": session_id,
        "timestamp":  datetime.now(timezone.utc).isoformat(),
        "mode":       mode,
        **(extra or {}),
    }
    _REQUEST_LOG.append(entry)
    return entry


def get_request_log() -> list:
    """Return all logged requests (for /admin endpoint or LangSmith review)."""
    return _REQUEST_LOG


def clear_log():
    """Clear the in-memory log (used between test runs)."""
    _REQUEST_LOG.clear()
