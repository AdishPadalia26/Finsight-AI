import re
from typing import List


_PII_PATTERNS = {
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b"),
    "account_number": re.compile(r"\baccount\s*(?:number|#|no\.?)\s*[:\-]?\s*\d{6,}\b", re.IGNORECASE),
    "routing_number": re.compile(r"\brouting\s*(?:number|#|no\.?)\s*[:\-]?\s*\d{9}\b", re.IGNORECASE),
}

_REDACTION_MAP = {
    "ssn": "[SSN REDACTED]",
    "credit_card": "[CARD REDACTED]",
    "account_number": "[ACCOUNT REDACTED]",
    "routing_number": "[ROUTING REDACTED]",
}


def detect_pii(text: str) -> List[str]:
    """Return list of PII type names found in text."""
    found = []
    for pii_type, pattern in _PII_PATTERNS.items():
        if pattern.search(text):
            found.append(pii_type)
    return found


def redact_pii(text: str) -> str:
    """Replace PII patterns with redaction placeholders."""
    for pii_type, pattern in _PII_PATTERNS.items():
        text = pattern.sub(_REDACTION_MAP[pii_type], text)
    return text


def has_pii(text: str) -> bool:
    return bool(detect_pii(text))
