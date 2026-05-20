"""
Math consistency unit tests for all 10 synthetic user profiles.

Run:
    pytest finsight-ai/tests/test_synthetic_data.py -v
    # or from finsight-ai/
    pytest tests/test_synthetic_data.py -v
"""

import pytest
from data.synthetic_users import (
    SYNTHETIC_USERS,
    get_user_by_id,
    get_users_by_risk,
    get_distressed_users,
    build_budget_input,
    build_goal_input,
    build_investment_input,
    build_debt_input,
    build_tax_input,
    build_life_event_input,
    build_advisor_input,
)


# ─────────────────────────────────────────────────────────────────────────────
# Test 1 — Expenses + debt payments do not exceed income for stable/thriving users
# ─────────────────────────────────────────────────────────────────────────────

def test_surplus_computation():
    """_computed.monthly_surplus == monthly_income - monthly_expenses - sum(min_payments)."""
    for u in SYNTHETIC_USERS:
        expected = (
            u["monthly_income"]
            - u["monthly_expenses"]
            - sum(d["minimum_payment"] for d in u["debts"])
        )
        actual = u["_computed"]["monthly_surplus"]
        assert abs(actual - expected) < 0.01, (
            f"{u['id']} ({u['name']}): surplus {actual} != expected {expected:.2f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 2 — Net worth = assets - liabilities
# ─────────────────────────────────────────────────────────────────────────────

def test_net_worth_computation():
    """_computed.net_worth == savings + investments + property_value - total_debt."""
    for u in SYNTHETIC_USERS:
        total_debt = sum(d["balance"] for d in u["debts"])
        expected = u["savings"] + u["investments"] + u["property_value"] - total_debt
        actual = u["_computed"]["net_worth"]
        assert abs(actual - expected) < 0.01, (
            f"{u['id']} ({u['name']}): net_worth {actual} != expected {expected:.2f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 3 — Savings rate = monthly_surplus / monthly_income
# ─────────────────────────────────────────────────────────────────────────────

def test_savings_rate_computation():
    """_computed.savings_rate == monthly_surplus / monthly_income."""
    for u in SYNTHETIC_USERS:
        surplus = u["_computed"]["monthly_surplus"]
        expected = surplus / u["monthly_income"] if u["monthly_income"] > 0 else 0.0
        actual = u["_computed"]["savings_rate"]
        assert abs(actual - round(expected, 4)) < 0.0001, (
            f"{u['id']} ({u['name']}): savings_rate {actual} != expected {expected:.4f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 4 — Emergency fund months = savings / monthly_expenses
# ─────────────────────────────────────────────────────────────────────────────

def test_emergency_fund_months_computation():
    """_computed.emergency_fund_months == savings / monthly_expenses."""
    for u in SYNTHETIC_USERS:
        expected = (u["savings"] / u["monthly_expenses"]) if u["monthly_expenses"] > 0 else 0.0
        actual = u["_computed"]["emergency_fund_months"]
        assert abs(actual - round(expected, 2)) < 0.01, (
            f"{u['id']} ({u['name']}): ef_months {actual} != expected {expected:.2f}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5 — Required financial invariants (special users)
# ─────────────────────────────────────────────────────────────────────────────

def test_required_invariants():
    """u04 negative surplus, u05 low savings rate, u09 EF < 1, u10 high savings rate."""
    u04 = get_user_by_id("u04")
    assert u04 is not None
    assert u04["_computed"]["monthly_surplus"] < 0, "u04 must have negative monthly surplus"

    u05 = get_user_by_id("u05")
    assert u05 is not None
    assert u05["_computed"]["savings_rate"] < 0.05, (
        f"u05 savings_rate {u05['_computed']['savings_rate']:.4f} must be < 0.05"
    )

    u09 = get_user_by_id("u09")
    assert u09 is not None
    assert u09["_computed"]["emergency_fund_months"] < 1.0, (
        f"u09 EF months {u09['_computed']['emergency_fund_months']:.2f} must be < 1.0"
    )

    u10 = get_user_by_id("u10")
    assert u10 is not None
    assert u10["_computed"]["savings_rate"] > 0.30, (
        f"u10 savings_rate {u10['_computed']['savings_rate']:.4f} must be > 0.30"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 6 — All agent input builders return required keys and correct types
# ─────────────────────────────────────────────────────────────────────────────

_REQUIRED_CORE_KEYS = {
    "session_id", "age", "location", "employment_status",
    "monthly_income", "monthly_expenses", "savings", "investments",
    "property_value", "debts", "goals", "risk_tolerance", "investment_horizon",
}

_BUILDER_EXTRA_KEYS: dict[str, set[str]] = {
    "budget":       {"tax_bracket", "_hint_monthly_surplus"},
    "goal":         {"_hint_monthly_surplus", "_hint_savings_rate", "_hint_net_worth"},
    "investment":   {"tax_bracket", "_hint_net_worth", "_hint_monthly_surplus"},
    "debt":         {"_hint_monthly_debt_payments", "_hint_monthly_surplus", "_hint_total_debt"},
    "tax":          {"tax_bracket", "_hint_net_worth"},
    "life_event":   {"recent_life_events", "tax_bracket", "_hint_net_worth", "_hint_monthly_surplus"},
    "advisor":      {"life_stage", "financial_health", "_hint_emergency_fund_months",
                     "_hint_savings_rate", "_hint_net_worth", "_hint_monthly_surplus"},
}

_BUILDERS = {
    "budget":     build_budget_input,
    "goal":       build_goal_input,
    "investment": build_investment_input,
    "debt":       build_debt_input,
    "tax":        build_tax_input,
    "life_event": build_life_event_input,
    "advisor":    build_advisor_input,
}


def test_agent_input_builders_keys():
    """Every builder returns all required core keys + its own extra keys."""
    for u in SYNTHETIC_USERS:
        for name, builder_fn in _BUILDERS.items():
            result = builder_fn(u)
            assert isinstance(result, dict), f"{u['id']} builder '{name}' did not return a dict"

            missing_core = _REQUIRED_CORE_KEYS - result.keys()
            assert not missing_core, (
                f"{u['id']} builder '{name}' missing core keys: {missing_core}"
            )

            for extra_key in _BUILDER_EXTRA_KEYS.get(name, set()):
                assert extra_key in result, (
                    f"{u['id']} builder '{name}' missing expected key '{extra_key}'"
                )

            # debts and goals must be lists
            assert isinstance(result["debts"], list), f"{u['id']} builder '{name}': debts not a list"
            assert isinstance(result["goals"], list), f"{u['id']} builder '{name}': goals not a list"


# ─────────────────────────────────────────────────────────────────────────────
# Test 7 — Lookup helpers work correctly
# ─────────────────────────────────────────────────────────────────────────────

def test_lookup_helpers():
    """get_user_by_id, get_users_by_risk, get_distressed_users return correct results."""
    # get_user_by_id — valid
    for uid in ["u01", "u05", "u10"]:
        user = get_user_by_id(uid)
        assert user is not None, f"get_user_by_id('{uid}') returned None"
        assert user["id"] == uid

    # get_user_by_id — nonexistent
    assert get_user_by_id("u99") is None

    # get_users_by_risk — all results match the requested tolerance
    for risk in ("conservative", "moderate", "aggressive"):
        results = get_users_by_risk(risk)
        assert isinstance(results, list)
        assert all(u["risk_tolerance"] == risk for u in results), (
            f"get_users_by_risk('{risk}') returned user with wrong tolerance"
        )

    # get_distressed_users — all results have distressed or struggling health
    distressed = get_distressed_users()
    assert len(distressed) >= 2, "Expected at least 2 distressed/struggling users"
    assert all(u["financial_health"] in ("distressed", "struggling") for u in distressed)

    # Coverage: 10 users total
    assert len(SYNTHETIC_USERS) == 10
