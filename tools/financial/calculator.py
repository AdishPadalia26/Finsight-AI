import math
import copy
from typing import List
import numpy_financial as npf


# ── Basic ratios ──────────────────────────────────────────────────────────────

def savings_rate(monthly_income: float, monthly_expenses: float) -> float:
    if monthly_income <= 0:
        return 0.0
    return round((monthly_income - monthly_expenses) / monthly_income * 100, 2)


def debt_to_income(monthly_debt_payments: float, monthly_income: float) -> float:
    if monthly_income <= 0:
        return 0.0
    return round(monthly_debt_payments / monthly_income * 100, 2)


def emergency_fund_months(savings: float, monthly_expenses: float) -> float:
    if monthly_expenses <= 0:
        return 0.0
    return round(savings / monthly_expenses, 2)


def net_worth(savings: float, investments: float, property_value: float, total_debt: float) -> float:
    return round((savings + investments + property_value) - total_debt, 2)


def total_minimum_debt_payments(debts: List[dict]) -> float:
    return sum(d.get("minimum_payment", 0) for d in debts)


def total_debt_balance(debts: List[dict]) -> float:
    return sum(d.get("balance", 0) for d in debts)


# ── Time-value calculations ───────────────────────────────────────────────────

def future_value(present_value: float, annual_rate: float, years: int) -> float:
    return round(float(npf.fv(annual_rate / 12, years * 12, 0, -present_value)), 2)


def monthly_payment(principal: float, annual_rate: float, years: int) -> float:
    if annual_rate == 0:
        return round(principal / (years * 12), 2)
    return round(float(-npf.pmt(annual_rate / 12, years * 12, principal)), 2)


def months_to_goal(
    target: float,
    current_savings: float,
    monthly_contribution: float,
    annual_rate: float = 0.05,
) -> float:
    if monthly_contribution <= 0:
        return float("inf")
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        return round((target - current_savings) / monthly_contribution, 1)
    try:
        n = math.log(
            (target * monthly_rate + monthly_contribution) /
            (current_savings * monthly_rate + monthly_contribution)
        ) / math.log(1 + monthly_rate)
        return round(n, 1)
    except (ValueError, ZeroDivisionError):
        return float("inf")


# ── Financial health scoring ──────────────────────────────────────────────────

def financial_health_score(sr: float, dti: float, emergency_months: float) -> dict:
    savings_score = min(sr / 20 * 40, 40)
    dti_score = max(0, (1 - dti / 50) * 30)
    emergency_score = min(emergency_months / 6 * 30, 30)
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


# ── Goal planning math ────────────────────────────────────────────────────────

def required_monthly_contribution(
    target: float,
    current_savings: float,
    months: int,
    annual_rate: float = 0.05,
) -> float:
    """Monthly contribution needed to reach target in given months from current_savings.

    npf sign convention: pv is negative (outflow/deposit), fv is positive (inflow/receipt).
    We use -current_savings as pv and target as fv so pmt comes back negative (deposit).
    Negating gives the positive monthly deposit amount.
    """
    if months <= 0:
        return 0.0
    if current_savings >= target:
        return 0.0
    monthly_rate = annual_rate / 12
    if monthly_rate == 0:
        shortfall = max(0.0, target - current_savings)
        return round(shortfall / months, 2)
    try:
        # pv = -current_savings (already have this much, negative = outflow already made)
        # fv = target (positive = what you receive)
        pmt = float(-npf.pmt(monthly_rate, months, -current_savings, target))
        return round(max(0.0, pmt), 2)
    except Exception:
        return round(max(0.0, (target - current_savings) / months), 2)


def goal_feasibility_score(required_monthly: float, available_monthly: float) -> float:
    """0–100 score where 100 = fully feasible with surplus to spare."""
    if required_monthly <= 0:
        return 100.0
    if available_monthly <= 0:
        return 0.0
    ratio = available_monthly / required_monthly
    return round(min(100.0, ratio * 100), 1)


def milestone_balances(
    current: float,
    monthly_contribution: float,
    annual_rate: float,
    months: int,
    checkpoints: int = 4,
) -> list:
    """Projected balances at evenly spaced checkpoints towards the goal."""
    monthly_rate = annual_rate / 12
    milestones = []
    for i in range(1, checkpoints + 1):
        m = int(months * i / checkpoints)
        if monthly_rate == 0:
            bal = current + monthly_contribution * m
        else:
            try:
                bal = float(npf.fv(monthly_rate, m, -monthly_contribution, -current))
            except Exception:
                bal = current + monthly_contribution * m
        milestones.append({"month": m, "balance": round(max(0.0, bal), 2)})
    return milestones


# ── Debt payoff simulation ────────────────────────────────────────────────────

def simulate_debt_payoff(
    debts: list,
    extra_monthly: float = 0.0,
    method: str = "avalanche",
) -> dict:
    """
    Simulates debt payoff using avalanche (highest rate first) or snowball
    (lowest balance first) with optional extra monthly payment.
    Returns interest paid, months to freedom, and payoff order.
    """
    if not debts or all(d.get("balance", 0) <= 0 for d in debts):
        return {
            "method": method,
            "months_to_debt_free": 0,
            "total_interest_paid": 0.0,
            "interest_saved_vs_minimum": 0.0,
            "payoff_order": [],
            "minimum_only_months": 0,
            "minimum_only_interest": 0.0,
        }

    def _run(debt_list: list, extra: float, ascending_balance: bool) -> dict:
        working = [
            {
                "type": d.get("type", "unknown"),
                "balance": float(d.get("balance", 0)),
                "rate_monthly": float(d.get("interest_rate", 0)) / 100.0 / 12.0,
                "min_pay": float(d.get("minimum_payment", 0)),
                "original_balance": float(d.get("balance", 0)),
                "paid_off_month": None,
            }
            for d in debt_list
            if d.get("balance", 0) > 0
        ]
        if not working:
            return {"months": 0, "total_interest": 0.0, "payoff_order": []}

        if ascending_balance:
            working.sort(key=lambda d: d["balance"])
        else:
            working.sort(key=lambda d: -d["rate_monthly"])

        total_interest = 0.0
        freed_minimum = 0.0

        for month in range(1, 601):
            active = [d for d in working if d["balance"] > 0]
            if not active:
                break
            target = active[0]
            for debt in working:
                if debt["balance"] <= 0:
                    continue
                interest = debt["balance"] * debt["rate_monthly"]
                total_interest += interest
                payment = debt["min_pay"]
                if debt is target:
                    payment += extra + freed_minimum
                payment = min(payment, debt["balance"] + interest)
                debt["balance"] = max(0.0, debt["balance"] + interest - payment)
                if debt["balance"] < 0.01:
                    debt["balance"] = 0.0
                    if debt["paid_off_month"] is None:
                        debt["paid_off_month"] = month
                        freed_minimum += debt["min_pay"]

        payoff_order = sorted(
            [
                {"type": d["type"], "month": d["paid_off_month"], "original_balance": d["original_balance"]}
                for d in working
                if d["paid_off_month"] is not None
            ],
            key=lambda x: x["month"],
        )
        final_month = max((d["paid_off_month"] or 0 for d in working), default=0)
        return {"months": final_month, "total_interest": round(total_interest, 2), "payoff_order": payoff_order}

    baseline = _run(debts, 0.0, ascending_balance=False)
    if method == "snowball":
        result = _run(debts, extra_monthly, ascending_balance=True)
    else:
        result = _run(debts, extra_monthly, ascending_balance=False)

    return {
        "method": method,
        "months_to_debt_free": result["months"],
        "total_interest_paid": result["total_interest"],
        "interest_saved_vs_minimum": round(max(0.0, baseline["total_interest"] - result["total_interest"]), 2),
        "payoff_order": result["payoff_order"],
        "minimum_only_months": baseline["months"],
        "minimum_only_interest": baseline["total_interest"],
    }


# ── Stress tests ──────────────────────────────────────────────────────────────

def stress_job_loss(
    monthly_income: float,
    monthly_expenses: float,
    savings: float,
    debts: list,
    months_without_income: int = 6,
) -> dict:
    """How long can the user survive without income?"""
    min_debt = total_minimum_debt_payments(debts)
    essential_burn = monthly_expenses + min_debt
    runway_months = round(savings / essential_burn, 1) if essential_burn > 0 else 999.0
    income_gap = round(monthly_income * months_without_income, 2)
    savings_gap = round(max(0.0, income_gap - savings), 2)
    ratio = min(runway_months / months_without_income, 1.5)
    score = min(10, max(1, round(ratio * 7)))
    return {
        "scenario": "JOB_LOSS",
        "runway_months": runway_months,
        "income_gap": income_gap,
        "savings_gap": savings_gap,
        "essential_monthly_burn": round(essential_burn, 2),
        "score": score,
        "assessment": "Strong" if score >= 7 else "Moderate" if score >= 5 else "Vulnerable",
    }


def stress_market_crash(
    investments: float,
    monthly_income: float,
    monthly_expenses: float,
    drawdown_pct: float = 0.30,
) -> dict:
    """30% portfolio drawdown: loss amount and recovery timeline."""
    loss = round(investments * drawdown_pct, 2)
    remaining = max(0.0, investments - loss)
    surplus = monthly_income - monthly_expenses
    try:
        recovery_months = round(
            math.log(investments / remaining) / math.log(1.0 + 0.08 / 12), 1
        ) if remaining > 1 else 120.0
    except Exception:
        recovery_months = 120.0
    income_to_recover = round(loss / surplus, 1) if surplus > 0 else 999.0
    score = 8 if surplus > monthly_expenses * 0.2 else 5
    if investments < monthly_income * 6:
        score = max(score - 2, 1)
    return {
        "scenario": "MARKET_CRASH",
        "portfolio_loss": loss,
        "remaining_portfolio": round(remaining, 2),
        "recovery_months_estimate": min(recovery_months, 120.0),
        "months_income_to_recover": min(income_to_recover, 120.0),
        "score": score,
        "assessment": "Strong" if score >= 7 else "Moderate" if score >= 5 else "Vulnerable",
    }


def stress_rate_spike(
    debts: list,
    monthly_income: float,
    monthly_expenses: float,
    rate_increase_pct: float = 3.0,
) -> dict:
    """3% rate increase impact on variable-rate debts."""
    variable_types = {"credit_card", "bnpl", "personal_loan", "auto"}
    variable_debts = [d for d in debts if d.get("type", "").lower() in variable_types]
    extra_monthly = sum(
        d.get("balance", 0) * rate_increase_pct / 100.0 / 12.0
        for d in variable_debts
    )
    new_min_payments = total_minimum_debt_payments(debts) + extra_monthly
    new_dti = debt_to_income(new_min_payments, monthly_income)
    surplus_after = round(monthly_income - monthly_expenses - extra_monthly, 2)
    score = min(10, max(1, round(10 - new_dti / 10)))
    return {
        "scenario": "RATE_SPIKE",
        "extra_monthly_cost": round(extra_monthly, 2),
        "new_dti_pct": round(new_dti, 2),
        "surplus_after_spike": surplus_after,
        "variable_debt_balance": round(sum(d.get("balance", 0) for d in variable_debts), 2),
        "score": score,
        "assessment": "Strong" if score >= 7 else "Moderate" if score >= 5 else "Vulnerable",
    }


def stress_medical_emergency(
    savings: float,
    monthly_income: float,
    expense_amount: float = 50000.0,
) -> dict:
    """$50k unexpected medical expense: can savings absorb it?"""
    coverage_ratio = savings / expense_amount if expense_amount > 0 else 0.0
    months_income_equivalent = round(expense_amount / monthly_income, 1) if monthly_income > 0 else 999.0
    shortfall = round(max(0.0, expense_amount - savings), 2)
    score = min(10, max(1, round(coverage_ratio * 10)))
    return {
        "scenario": "MEDICAL_EMERGENCY",
        "expense_amount": expense_amount,
        "savings_available": savings,
        "shortfall": shortfall,
        "coverage_ratio": round(coverage_ratio, 2),
        "months_income_equivalent": months_income_equivalent,
        "score": score,
        "assessment": "Strong" if score >= 7 else "Moderate" if score >= 5 else "Vulnerable",
    }


def stress_inflation_spike(
    monthly_income: float,
    monthly_expenses: float,
    debts: list,
    inflation_rate: float = 0.08,
) -> dict:
    """8% inflation spike: can surplus absorb the cost-of-living increase?"""
    extra_monthly = round(monthly_expenses * inflation_rate, 2)
    min_debt = total_minimum_debt_payments(debts)
    new_surplus = round(monthly_income - monthly_expenses - min_debt - extra_monthly, 2)
    surplus_before = round(monthly_income - monthly_expenses - min_debt, 2)
    ratio = new_surplus / monthly_income if monthly_income > 0 else 0.0
    score = min(10, max(1, round((ratio + 0.1) * 20)))
    return {
        "scenario": "INFLATION_SPIKE",
        "inflation_rate_pct": round(inflation_rate * 100, 1),
        "extra_monthly_cost": extra_monthly,
        "surplus_before": surplus_before,
        "surplus_after": new_surplus,
        "income_erosion_pct": round((extra_monthly / monthly_income * 100) if monthly_income > 0 else 0, 1),
        "score": score,
        "assessment": "Strong" if score >= 7 else "Moderate" if score >= 5 else "Vulnerable",
    }


def compute_stress_tests(
    monthly_income: float,
    monthly_expenses: float,
    savings: float,
    investments: float,
    debts: list,
) -> dict:
    """Run all 5 stress scenarios and return combined results with summary scores."""
    jl = stress_job_loss(monthly_income, monthly_expenses, savings, debts)
    mc = stress_market_crash(investments, monthly_income, monthly_expenses)
    rs = stress_rate_spike(debts, monthly_income, monthly_expenses)
    me = stress_medical_emergency(savings, monthly_income)
    inf = stress_inflation_spike(monthly_income, monthly_expenses, debts)
    scenario_map = {
        "JOB_LOSS": jl,
        "MARKET_CRASH": mc,
        "MEDICAL_EMERGENCY": me,
        "RATE_SPIKE": rs,
        "INFLATION_SPIKE": inf,
    }
    scores = [s["score"] for s in scenario_map.values()]
    avg = round(sum(scores) / len(scores), 1)
    min_score = min(scores)
    weakest = min(scenario_map, key=lambda k: scenario_map[k]["score"])
    return {
        "scenarios": scenario_map,
        "summary": {
            "average_score": avg,
            "minimum_score": min_score,
            "overall_resilience": "Strong" if avg >= 7 else "Moderate" if avg >= 5 else "Vulnerable",
            "weakest_scenario": weakest,
        },
    }
