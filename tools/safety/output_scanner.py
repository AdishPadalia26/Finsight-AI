import re
from typing import TypedDict, List


class ScanResult(TypedDict):
    severity: str           # "CRITICAL", "MODERATE", "CLEAN"
    violations: List[dict]  # each: {type, severity, matched_text, rule}


# ── CRITICAL rules — hard stop, no output delivered ──────────────────────────
_CRITICAL_RULES = [
    {
        "rule": "guaranteed_return",
        "pattern": re.compile(
            r"\b(guaranteed?\s+return|guaranteed?\s+\d+%|risk[- ]free\s+profit|"
            r"will\s+definitely\s+earn|certain\s+return|100%\s+safe\s+investment)\b",
            re.IGNORECASE,
        ),
    },
    {
        "rule": "specific_stock_ticker",
        # Matches $AAPL-style tickers — not ETF category descriptions
        "pattern": re.compile(r"\$[A-Z]{2,5}\b"),
    },
    {
        "rule": "unlicensed_tax_advice",
        "pattern": re.compile(
            r"\b(you\s+owe\s+\$[\d,]+\s+in\s+taxes|your\s+tax\s+liability\s+is\s+\$|"
            r"you\s+must\s+file\s+form)\b",
            re.IGNORECASE,
        ),
    },
    {
        "rule": "unlicensed_legal_advice",
        "pattern": re.compile(
            r"\b(you\s+are\s+legally\s+required|this\s+is\s+not\s+legal\s+advice\s+but\s+you\s+must)\b",
            re.IGNORECASE,
        ),
    },
]

# ── MODERATE rules — rewrite required before delivery ────────────────────────
_MODERATE_RULES = [
    {
        "rule": "should_buy",
        "pattern": re.compile(r"\byou\s+should\s+buy\b", re.IGNORECASE),
        "replacement": "you may want to consider",
    },
    {
        "rule": "best_investment",
        "pattern": re.compile(r"\bthe?\s+best\s+investment\s+is\b", re.IGNORECASE),
        "replacement": "one strong approach to consider is",
    },
    {
        "rule": "will_definitely",
        "pattern": re.compile(r"\bwill\s+definitely\b", re.IGNORECASE),
        "replacement": "has historically",
    },
    {
        "rule": "i_recommend_purchasing",
        "pattern": re.compile(r"\bI\s+recommend\s+purchasing\b", re.IGNORECASE),
        "replacement": "one option to explore is purchasing",
    },
    {
        "rule": "bare_return_percentage",
        # Catches "returns 12%" without any caveat language nearby
        "pattern": re.compile(r"\breturns?\s+\d+(\.\d+)?%(?!\s*(historically|on average|per year on average))\b", re.IGNORECASE),
        "replacement": None,  # handled by llm rewrite — too context-sensitive for simple replace
    },
]


def scan_output(text: str) -> ScanResult:
    """
    Scan text for compliance violations.
    Returns ScanResult with severity CRITICAL, MODERATE, or CLEAN.
    Never raises — caller decides what to do with severity.
    """
    violations: List[dict] = []

    for rule in _CRITICAL_RULES:
        match = rule["pattern"].search(text)
        if match:
            violations.append({
                "type": rule["rule"],
                "severity": "CRITICAL",
                "matched_text": match.group(0),
            })

    for rule in _MODERATE_RULES:
        match = rule["pattern"].search(text)
        if match:
            violations.append({
                "type": rule["rule"],
                "severity": "MODERATE",
                "matched_text": match.group(0),
                "replacement": rule.get("replacement"),
            })

    critical = any(v["severity"] == "CRITICAL" for v in violations)
    moderate = any(v["severity"] == "MODERATE" for v in violations)

    severity = "CRITICAL" if critical else ("MODERATE" if moderate else "CLEAN")

    return ScanResult(severity=severity, violations=violations)


def apply_moderate_rewrites(text: str) -> str:
    """Apply simple string replacements for all MODERATE rules that have a replacement."""
    for rule in _MODERATE_RULES:
        if rule.get("replacement"):
            text = rule["pattern"].sub(rule["replacement"], text)
    return text
