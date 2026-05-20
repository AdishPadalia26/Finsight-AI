"""
Synthetic financial user profiles for testing FinSight AI agents.

10 financially diverse users spanning early career → pre-retirement,
distressed → thriving, zero debt → heavy debt.

Usage:
    from data.synthetic_users import SYNTHETIC_USERS, get_user_by_id, build_budget_input
"""

from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Helper — build a profile dict in the same schema as mock_profiles.py / state.py
# ─────────────────────────────────────────────────────────────────────────────

def _profile(
    uid: str,
    name: str,
    age: int,
    location: str,
    employment_status: str,
    monthly_income: float,
    monthly_expenses: float,
    savings: float,
    investments: float,
    property_value: float,
    debts: list,
    goals: list,
    risk_tolerance: str,
    investment_horizon: int,
    credit_score: int,
    tax_bracket: float,
    life_stage: str,
    financial_health: str,
    life_events: list,
    notes: str,
) -> dict:
    """Compose a full profile dict, computing derived fields automatically."""
    total_debt = sum(d["balance"] for d in debts)
    monthly_debt_payments = sum(d["minimum_payment"] for d in debts)
    monthly_surplus = monthly_income - monthly_expenses - monthly_debt_payments
    net_worth = savings + investments + property_value - total_debt
    savings_rate = (monthly_surplus / monthly_income) if monthly_income > 0 else 0.0
    emergency_fund_months = (savings / monthly_expenses) if monthly_expenses > 0 else 0.0

    return {
        # Identity
        "id": uid,
        "name": name,
        # Pipeline fields (mirrors FinancialProfile TypedDict)
        "session_id": f"synthetic-{uid}",
        "revision_count": 0,
        "pipeline_errors": [],
        "raw_input": None,
        # Demographics
        "age": age,
        "location": location,
        "employment_status": employment_status,
        # Income & expenses
        "monthly_income": monthly_income,
        "monthly_expenses": monthly_expenses,
        # Assets
        "savings": savings,
        "investments": investments,
        "property_value": property_value,
        # Debts
        "debts": debts,
        # Goals
        "goals": goals,
        # Risk & preferences
        "risk_tolerance": risk_tolerance,
        "investment_horizon": investment_horizon,
        # User-provided hints
        "credit_score": credit_score,
        # Tax context
        "tax_bracket": tax_bracket,
        # Life events (for life_event agent)
        "recent_life_events": life_events,
        # Classification metadata
        "life_stage": life_stage,           # early_career | mid_career | peak_earning | pre_retirement
        "financial_health": financial_health,  # distressed | struggling | stable | thriving
        "notes": notes,
        # Computed fields (pre-calculated for test assertions)
        "_computed": {
            "total_debt": round(total_debt, 2),
            "monthly_debt_payments": round(monthly_debt_payments, 2),
            "monthly_surplus": round(monthly_surplus, 2),
            "net_worth": round(net_worth, 2),
            "savings_rate": round(savings_rate, 4),
            "emergency_fund_months": round(emergency_fund_months, 2),
        },
        # Agent output slots (None until pipeline fills them)
        "behavioral_fingerprint": None,
        "budget_recommendation": None,
        "goal_roadmap": None,
        "investment_strategy": None,
        "tax_opportunities": None,
        "debt_roadmap": None,
        "stress_tests": None,
        "personalised_advice": None,
        "critic_scores": None,
        "final_report": None,
        "compliance_audit": None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# User 1 — Fresh Graduate, Distressed
# Name: Priya Nair | Age: 23 | Austin, TX | student_loan + credit_card
# ─────────────────────────────────────────────────────────────────────────────
USER_01 = _profile(
    uid="u01",
    name="Priya Nair",
    age=23,
    location="Austin, TX",
    employment_status="full_time",
    monthly_income=3800.0,
    monthly_expenses=3100.0,
    savings=1200.0,
    investments=0.0,
    property_value=0.0,
    debts=[
        {"type": "student_loan", "balance": 32000.0, "interest_rate": 6.8, "minimum_payment": 310.0},
        {"type": "credit_card",  "balance": 4500.0,  "interest_rate": 24.9, "minimum_payment": 120.0},
    ],
    goals=[
        {"description": "Pay off credit card",    "target_amount": 4500.0,  "timeline_months": 12, "priority": "critical"},
        {"description": "Build emergency fund",   "target_amount": 9300.0,  "timeline_months": 24, "priority": "high"},
    ],
    risk_tolerance="conservative",
    investment_horizon=40,
    credit_score=610,
    tax_bracket=0.12,
    life_stage="early_career",
    financial_health="distressed",
    life_events=["new_job"],
    notes="Entry-level software dev, high debt-to-income, minimal cushion",
)

# ─────────────────────────────────────────────────────────────────────────────
# User 2 — Young Professional, Struggling
# Name: Marcus Thompson | Age: 26 | Chicago, IL | student_loan + auto
# ─────────────────────────────────────────────────────────────────────────────
USER_02 = _profile(
    uid="u02",
    name="Marcus Thompson",
    age=26,
    location="Chicago, IL",
    employment_status="full_time",
    monthly_income=5200.0,
    monthly_expenses=3900.0,
    savings=4500.0,
    investments=1500.0,
    property_value=0.0,
    debts=[
        {"type": "student_loan", "balance": 22000.0, "interest_rate": 5.0,  "minimum_payment": 230.0},
        {"type": "auto_loan",    "balance": 14000.0, "interest_rate": 7.2,  "minimum_payment": 285.0},
    ],
    goals=[
        {"description": "Emergency fund (3 months)",  "target_amount": 11700.0, "timeline_months": 18, "priority": "high"},
        {"description": "Start investing in Roth IRA", "target_amount": 7000.0,  "timeline_months": 12, "priority": "medium"},
    ],
    risk_tolerance="moderate",
    investment_horizon=37,
    credit_score=680,
    tax_bracket=0.22,
    life_stage="early_career",
    financial_health="struggling",
    life_events=[],
    notes="Marketing analyst, manageable debt load, needs to start investing",
)

# ─────────────────────────────────────────────────────────────────────────────
# User 3 — Mid-Career, Stable
# Name: Sofia Ramirez | Age: 34 | Denver, CO | mortgage only
# ─────────────────────────────────────────────────────────────────────────────
USER_03 = _profile(
    uid="u03",
    name="Sofia Ramirez",
    age=34,
    location="Denver, CO",
    employment_status="full_time",
    monthly_income=7800.0,
    monthly_expenses=4400.0,
    savings=22000.0,
    investments=35000.0,
    property_value=380000.0,
    debts=[
        {"type": "mortgage", "balance": 295000.0, "interest_rate": 3.25, "minimum_payment": 1280.0},
    ],
    goals=[
        {"description": "Pay off mortgage early (age 50)",  "target_amount": 295000.0, "timeline_months": 192, "priority": "medium"},
        {"description": "Kids college fund",                 "target_amount": 80000.0,  "timeline_months": 168, "priority": "high"},
        {"description": "Increase 401k to 15%",             "target_amount": 14040.0,  "timeline_months": 12,  "priority": "high"},
    ],
    risk_tolerance="moderate",
    investment_horizon=28,
    credit_score=750,
    tax_bracket=0.22,
    life_stage="mid_career",
    financial_health="stable",
    life_events=["had_child"],
    notes="UX designer, homeowner, starting to think long-term",
)

# ─────────────────────────────────────────────────────────────────────────────
# User 4 — Negative Surplus (MUST have monthly_surplus < 0)
# Name: Devon Clarke | Age: 31 | Miami, FL | heavy CC + auto + personal loan
# ─────────────────────────────────────────────────────────────────────────────
USER_04 = _profile(
    uid="u04",
    name="Devon Clarke",
    age=31,
    location="Miami, FL",
    employment_status="part_time",
    monthly_income=3600.0,
    monthly_expenses=3200.0,    # expenses + debt payments > income → negative surplus
    savings=800.0,
    investments=0.0,
    property_value=0.0,
    debts=[
        {"type": "credit_card",   "balance": 9800.0,  "interest_rate": 26.9, "minimum_payment": 245.0},
        {"type": "auto_loan",     "balance": 18000.0, "interest_rate": 11.5, "minimum_payment": 420.0},
        {"type": "personal_loan", "balance": 5000.0,  "interest_rate": 18.0, "minimum_payment": 150.0},
    ],
    goals=[
        {"description": "Stop going deeper into debt",  "target_amount": 0.0,     "timeline_months": 6,   "priority": "critical"},
        {"description": "Build $1,000 emergency buffer", "target_amount": 1000.0, "timeline_months": 12,  "priority": "critical"},
    ],
    risk_tolerance="conservative",
    investment_horizon=32,
    credit_score=560,
    tax_bracket=0.12,
    life_stage="mid_career",
    financial_health="distressed",
    life_events=["job_loss", "divorce"],
    notes="Part-time gig work, negative cash flow, urgent debt crisis",
)

# ─────────────────────────────────────────────────────────────────────────────
# User 5 — Very Low Savings Rate (MUST have savings_rate < 0.05)
# Name: Tyler Nguyen | Age: 29 | Los Angeles, CA | lifestyle inflation
# ─────────────────────────────────────────────────────────────────────────────
USER_05 = _profile(
    uid="u05",
    name="Tyler Nguyen",
    age=29,
    location="Los Angeles, CA",
    employment_status="full_time",
    monthly_income=8500.0,
    monthly_expenses=7900.0,   # very high relative to income → savings_rate ~0.01 after min payments
    savings=6000.0,
    investments=4000.0,
    property_value=0.0,
    debts=[
        {"type": "student_loan", "balance": 18000.0, "interest_rate": 4.5, "minimum_payment": 190.0},
        {"type": "credit_card",  "balance": 2200.0,  "interest_rate": 21.0, "minimum_payment": 55.0},
    ],
    goals=[
        {"description": "European vacation fund", "target_amount": 8000.0,  "timeline_months": 18, "priority": "medium"},
        {"description": "Down payment — condo",   "target_amount": 90000.0, "timeline_months": 60, "priority": "high"},
    ],
    risk_tolerance="moderate",
    investment_horizon=34,
    credit_score=695,
    tax_bracket=0.22,
    life_stage="early_career",
    financial_health="struggling",
    life_events=[],
    notes="Digital marketer in LA, lifestyle creep, technically solvent but barely saving",
)

# ─────────────────────────────────────────────────────────────────────────────
# User 6 — Mid-Career, Stable, Self-Employed
# Name: Ananya Krishnan | Age: 38 | Seattle, WA | mortgage + student loan
# ─────────────────────────────────────────────────────────────────────────────
USER_06 = _profile(
    uid="u06",
    name="Ananya Krishnan",
    age=38,
    location="Seattle, WA",
    employment_status="self_employed",
    monthly_income=11500.0,
    monthly_expenses=6000.0,
    savings=45000.0,
    investments=88000.0,
    property_value=620000.0,
    debts=[
        {"type": "mortgage",     "balance": 420000.0, "interest_rate": 3.75, "minimum_payment": 1950.0},
        {"type": "student_loan", "balance": 15000.0,  "interest_rate": 5.0,  "minimum_payment": 160.0},
    ],
    goals=[
        {"description": "SEP-IRA max contribution",  "target_amount": 66000.0,  "timeline_months": 12,  "priority": "high"},
        {"description": "Rental property purchase",  "target_amount": 100000.0, "timeline_months": 36,  "priority": "medium"},
        {"description": "Kids private school fund",  "target_amount": 120000.0, "timeline_months": 108, "priority": "high"},
    ],
    risk_tolerance="moderate",
    investment_horizon=24,
    credit_score=760,
    tax_bracket=0.24,
    life_stage="mid_career",
    financial_health="stable",
    life_events=["had_child"],
    notes="Freelance consultant, variable income, needs tax optimization",
)

# ─────────────────────────────────────────────────────────────────────────────
# User 7 — Peak Earning, Thriving, Zero Debt
# Name: James Okafor | Age: 44 | New York, NY | no debt at all
# ─────────────────────────────────────────────────────────────────────────────
USER_07 = _profile(
    uid="u07",
    name="James Okafor",
    age=44,
    location="New York, NY",
    employment_status="full_time",
    monthly_income=22000.0,
    monthly_expenses=9500.0,
    savings=80000.0,
    investments=320000.0,
    property_value=950000.0,
    debts=[],   # zero debt — mortgage paid off, no other obligations
    goals=[
        {"description": "Retire at 55 (FatFIRE)",    "target_amount": 4000000.0, "timeline_months": 132, "priority": "critical"},
        {"description": "Vacation home — Hamptons",  "target_amount": 400000.0,  "timeline_months": 60,  "priority": "medium"},
        {"description": "Charitable foundation seed", "target_amount": 250000.0,  "timeline_months": 84,  "priority": "low"},
    ],
    risk_tolerance="aggressive",
    investment_horizon=11,
    credit_score=820,
    tax_bracket=0.37,
    life_stage="peak_earning",
    financial_health="thriving",
    life_events=[],
    notes="SVP at investment bank, debt-free, focus on wealth accumulation + tax efficiency",
)

# ─────────────────────────────────────────────────────────────────────────────
# User 8 — Peak Earning, Stable, Mixed Debt
# Name: Lisa Chen | Age: 47 | Boston, MA | mortgage + HELOC
# ─────────────────────────────────────────────────────────────────────────────
USER_08 = _profile(
    uid="u08",
    name="Lisa Chen",
    age=47,
    location="Boston, MA",
    employment_status="full_time",
    monthly_income=16500.0,
    monthly_expenses=7800.0,
    savings=55000.0,
    investments=210000.0,
    property_value=880000.0,
    debts=[
        {"type": "mortgage", "balance": 320000.0, "interest_rate": 2.75, "minimum_payment": 1380.0},
        {"type": "heloc",    "balance": 45000.0,  "interest_rate": 8.5,  "minimum_payment": 320.0},
    ],
    goals=[
        {"description": "Retire at 62",            "target_amount": 3000000.0, "timeline_months": 180, "priority": "critical"},
        {"description": "Pay off HELOC",            "target_amount": 45000.0,   "timeline_months": 24,  "priority": "high"},
        {"description": "Max HSA contributions",   "target_amount": 8300.0,    "timeline_months": 12,  "priority": "medium"},
    ],
    risk_tolerance="moderate",
    investment_horizon=15,
    credit_score=795,
    tax_bracket=0.32,
    life_stage="peak_earning",
    financial_health="stable",
    life_events=["college_tuition"],
    notes="Healthcare administrator, sending first kid to college, strong net worth",
)

# ─────────────────────────────────────────────────────────────────────────────
# User 9 — Emergency Fund < 1 Month (MUST have emergency_fund_months < 1.0)
# Name: Roberto Vega | Age: 52 | Phoenix, AZ | near-retirement, cash-poor
# ─────────────────────────────────────────────────────────────────────────────
USER_09 = _profile(
    uid="u09",
    name="Roberto Vega",
    age=52,
    location="Phoenix, AZ",
    employment_status="full_time",
    monthly_income=14000.0,
    monthly_expenses=10500.0,   # savings = 8000 → emergency_fund_months = 8000/10500 ≈ 0.76
    savings=8000.0,
    investments=145000.0,
    property_value=510000.0,
    debts=[
        {"type": "mortgage",   "balance": 190000.0, "interest_rate": 4.0,  "minimum_payment": 910.0},
        {"type": "auto_loan",  "balance": 22000.0,  "interest_rate": 6.9,  "minimum_payment": 430.0},
        {"type": "credit_card","balance": 12000.0,  "interest_rate": 23.5, "minimum_payment": 300.0},
    ],
    goals=[
        {"description": "Retire at 65 — $1.5M target",  "target_amount": 1500000.0, "timeline_months": 156, "priority": "critical"},
        {"description": "Build 6-month emergency fund",  "target_amount": 63000.0,   "timeline_months": 24,  "priority": "critical"},
        {"description": "Clear credit card debt",        "target_amount": 12000.0,   "timeline_months": 18,  "priority": "high"},
    ],
    risk_tolerance="conservative",
    investment_horizon=13,
    credit_score=650,
    tax_bracket=0.24,
    life_stage="pre_retirement",
    financial_health="struggling",
    life_events=["medical_expense"],
    notes="Operations manager, medical bills drained cash, invested but illiquid, retirement risk",
)

# ─────────────────────────────────────────────────────────────────────────────
# User 10 — High Savings Rate (MUST have savings_rate > 0.30), FIRE path
# Name: Wei Zhang | Age: 36 | Austin, TX | zero consumer debt, aggressive saver
# ─────────────────────────────────────────────────────────────────────────────
USER_10 = _profile(
    uid="u10",
    name="Wei Zhang",
    age=36,
    location="Austin, TX",
    employment_status="full_time",
    monthly_income=18000.0,
    monthly_expenses=5500.0,   # low expenses → surplus = 12500 → savings_rate ≈ 0.694
    savings=95000.0,
    investments=420000.0,
    property_value=0.0,
    debts=[],   # no debt — house is rented intentionally for flexibility
    goals=[
        {"description": "FIRE at 45 — $3M portfolio",   "target_amount": 3000000.0, "timeline_months": 108, "priority": "critical"},
        {"description": "Crypto allocation (5% port.)",  "target_amount": 21000.0,   "timeline_months": 6,   "priority": "low"},
        {"description": "Angel investing fund",          "target_amount": 50000.0,   "timeline_months": 24,  "priority": "medium"},
    ],
    risk_tolerance="aggressive",
    investment_horizon=9,
    credit_score=800,
    tax_bracket=0.32,
    life_stage="mid_career",
    financial_health="thriving",
    life_events=[],
    notes="Staff engineer at tech startup, extreme saver, FIRE-focused, crypto dabbler",
)

# ─────────────────────────────────────────────────────────────────────────────
# Master list
# ─────────────────────────────────────────────────────────────────────────────

SYNTHETIC_USERS: list[dict] = [
    USER_01, USER_02, USER_03, USER_04, USER_05,
    USER_06, USER_07, USER_08, USER_09, USER_10,
]


# ─────────────────────────────────────────────────────────────────────────────
# Lookup helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_user_by_id(uid: str) -> dict | None:
    """Return a user profile by uid (e.g. 'u01')."""
    return next((u for u in SYNTHETIC_USERS if u["id"] == uid), None)


def get_users_by_risk(risk: str) -> list[dict]:
    """Return all users with the given risk_tolerance."""
    return [u for u in SYNTHETIC_USERS if u["risk_tolerance"] == risk]


def get_distressed_users() -> list[dict]:
    """Return all users classified as distressed or struggling."""
    return [u for u in SYNTHETIC_USERS if u["financial_health"] in ("distressed", "struggling")]


# ─────────────────────────────────────────────────────────────────────────────
# Agent input builders
# Each function strips metadata and returns only the fields each agent needs.
# ─────────────────────────────────────────────────────────────────────────────

def _core(user: dict) -> dict[str, Any]:
    """Common demographic + financial fields used by most agents."""
    return {
        "session_id":        user["session_id"],
        "age":               user["age"],
        "location":          user["location"],
        "employment_status": user["employment_status"],
        "monthly_income":    user["monthly_income"],
        "monthly_expenses":  user["monthly_expenses"],
        "savings":           user["savings"],
        "investments":       user["investments"],
        "property_value":    user["property_value"],
        "debts":             user["debts"],
        "goals":             user["goals"],
        "risk_tolerance":    user["risk_tolerance"],
        "investment_horizon": user["investment_horizon"],
        "credit_score":      user.get("credit_score"),
    }


def build_budget_input(user: dict) -> dict[str, Any]:
    """Input dict for Tier-2 BudgetArchitect agent."""
    base = _core(user)
    base.update({
        "tax_bracket":         user.get("tax_bracket"),
        "recent_life_events":  user.get("recent_life_events", []),
        # Include pre-computed surplus so the agent can validate its own math
        "_hint_monthly_surplus": user["_computed"]["monthly_surplus"],
    })
    return base


def build_goal_input(user: dict) -> dict[str, Any]:
    """Input dict for Tier-2 GoalEngineer agent."""
    base = _core(user)
    base.update({
        "_hint_monthly_surplus":  user["_computed"]["monthly_surplus"],
        "_hint_savings_rate":     user["_computed"]["savings_rate"],
        "_hint_net_worth":        user["_computed"]["net_worth"],
    })
    return base


def build_investment_input(user: dict) -> dict[str, Any]:
    """Input dict for Tier-2 InvestmentStrategist agent."""
    base = _core(user)
    base.update({
        "tax_bracket":            user.get("tax_bracket"),
        "recent_life_events":     user.get("recent_life_events", []),
        "_hint_net_worth":        user["_computed"]["net_worth"],
        "_hint_monthly_surplus":  user["_computed"]["monthly_surplus"],
    })
    return base


def build_debt_input(user: dict) -> dict[str, Any]:
    """Input dict for Tier-2 DebtElimination agent."""
    base = _core(user)
    base.update({
        "credit_score":                     user.get("credit_score"),
        "_hint_monthly_debt_payments":      user["_computed"]["monthly_debt_payments"],
        "_hint_monthly_surplus":            user["_computed"]["monthly_surplus"],
        "_hint_total_debt":                 user["_computed"]["total_debt"],
    })
    return base


def build_tax_input(user: dict) -> dict[str, Any]:
    """Input dict for Tier-2 TaxIntelligence agent."""
    base = _core(user)
    base.update({
        "tax_bracket":        user.get("tax_bracket"),
        "employment_status":  user["employment_status"],
        "recent_life_events": user.get("recent_life_events", []),
        "_hint_net_worth":    user["_computed"]["net_worth"],
    })
    return base


def build_life_event_input(user: dict) -> dict[str, Any]:
    """Input dict for Tier-3 LifeEventAgent."""
    base = _core(user)
    base.update({
        "recent_life_events": user.get("recent_life_events", []),
        "tax_bracket":        user.get("tax_bracket"),
        "_hint_net_worth":    user["_computed"]["net_worth"],
        "_hint_monthly_surplus": user["_computed"]["monthly_surplus"],
    })
    return base


def build_advisor_input(user: dict) -> dict[str, Any]:
    """Input dict for Tier-3 PersonalisedAdvisor agent."""
    base = _core(user)
    base.update({
        "tax_bracket":            user.get("tax_bracket"),
        "recent_life_events":     user.get("recent_life_events", []),
        "life_stage":             user.get("life_stage"),
        "financial_health":       user.get("financial_health"),
        "_hint_emergency_fund_months": user["_computed"]["emergency_fund_months"],
        "_hint_savings_rate":          user["_computed"]["savings_rate"],
        "_hint_net_worth":             user["_computed"]["net_worth"],
        "_hint_monthly_surplus":       user["_computed"]["monthly_surplus"],
    })
    return base
