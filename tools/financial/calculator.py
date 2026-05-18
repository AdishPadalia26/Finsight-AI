from typing import List
import numpy_financial as npf


# ── Basic ratios ──────────────────────────────────────────────────────────────

def savings_rate(monthly_income: float, monthly_expenses: float) -> float:
    """Percentage of income saved each month."""
    if monthly_income <= 0:
        return 0.0
    return round((monthly_income - monthly_expenses) / monthly_income * 100, 2)


def debt_to_income(monthly_debt_payments: float, monthly_income: float) -> float:
    """Total monthly debt payments as a percentage of gross monthly income."""
    if monthly_income <= 0:
        return 0.0
    return round(monthly_debt_payments / monthly_income * 100, 2)


def emergency_fund_months(savings: float, monthly_expenses: float) -> float:
    """How many months of expenses the current savings covers."""
    if monthly_expenses <= 0:
        return 0.0
    return round(savings / monthly_expenses, 2)


def net_worth(
    savings: float,
    investments: float,
    property_value: float,
    total_debt: float,
) -> float:
    return round((savings + investments + property_value) - total_debt, 2)


def total_minimum_debt_payments(debts: List[dict]) -> float:
    return sum(d.get("minimum_payment", 0) for d in debts)


def total_debt_balance(debts: List[dict]) -> float:
    return sum(d.get("balance", 0) for d in debts)


# ── Time-value calculations ───────────────────────────────────────────────────

def future_value(present_value: float, annual_rate: float, years: int) -> float:
    """Compound growth of a lump sum."""
    return round(float(npf.fv(annual_rate / 12, years * 12, 0, -present_value)), 2)


def monthly_payment(principal: float, annual_rate: float, years: int) -> float:
    """Fixed monthly payment to pay off a loan."""
    if annual_rate == 0:
        return round(principal / (years * 12), 2)
    return round(float(-npf.pmt(annual_rate / 12, years * 12, principal)), 2)


def months_to_goal(
    target: float,
    current_savings: float,
    monthly_contribution: float,
    annual_rate: float = 0.05,
) -> float:
    """Months needed to reach a savings target given regular contributions."""
    if monthly_contribution <= 0:
        return float("inf")
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return round((target - current_savings) / monthly_contribution, 1)
    # Solve FV formula for n
    import math
    try:
        n = math.log(
            (target * monthly_rate + monthly_contribution) /
            (current_savings * monthly_rate + monthly_contribution)
        ) / math.log(1 + monthly_rate)
        return round(n, 1)
    except (ValueError, ZeroDivisionError):
        return float("inf")


# ── Financial health scoring ──────────────────────────────────────────────────

def financial_health_score(
    sr: float,          # savings rate %
    dti: float,         # debt-to-income %
    emergency_months: float,
) -> dict:
    """
    Returns a score 0–100 broken down across three dimensions.
    Benchmarks: savings rate >= 20% is ideal, DTI <= 36% is healthy,
    emergency fund >= 6 months is ideal.
    """
    savings_score = min(sr / 20 * 40, 40)           # max 40 pts
    dti_score = max(0, (1 - dti / 50) * 30)         # max 30 pts
    emergency_score = min(emergency_months / 6 * 30, 30)  # max 30 pts

    total = round(savings_score + dti_score + emergency_score, 1)

    return {
        "total": total,
        "savings_score": round(savings_score, 1),
        "dti_score": round(dti_score, 1),
        "emergency_score": round(emergency_score, 1),
        "grade": _grade(total),
    }


def _grade(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    if score >= 35:
        return "D"
    return "F"
