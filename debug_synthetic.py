"""
10×7 agent test matrix — runs all 7 agent input builders against all 10 users.
Prints a pass/fail grid (70 cases total) and a per-user summary.

Run from finsight-ai/:
    python debug_synthetic.py
"""

import sys
import traceback
from data.synthetic_users import (
    SYNTHETIC_USERS,
    build_budget_input,
    build_goal_input,
    build_investment_input,
    build_debt_input,
    build_tax_input,
    build_life_event_input,
    build_advisor_input,
)

BUILDERS = {
    "budget":      build_budget_input,
    "goal":        build_goal_input,
    "investment":  build_investment_input,
    "debt":        build_debt_input,
    "tax":         build_tax_input,
    "life_event":  build_life_event_input,
    "advisor":     build_advisor_input,
}

REQUIRED_CORE = {
    "session_id", "age", "location", "employment_status",
    "monthly_income", "monthly_expenses", "savings", "investments",
    "property_value", "debts", "goals", "risk_tolerance", "investment_horizon",
}

# ANSI
_GREEN = "\033[92m"
_RED   = "\033[91m"
_CYAN  = "\033[96m"
_BOLD  = "\033[1m"
_RESET = "\033[0m"

_PASS = f"{_GREEN}PASS{_RESET}"
_FAIL = f"{_RED}FAIL{_RESET}"


def _check(user: dict, builder_name: str, builder_fn) -> tuple[bool, str]:
    """Run one builder, return (passed, error_message)."""
    try:
        result = builder_fn(user)
    except Exception as e:
        return False, f"Exception: {e}\n{traceback.format_exc()}"

    if not isinstance(result, dict):
        return False, f"returned {type(result).__name__}, expected dict"

    missing = REQUIRED_CORE - result.keys()
    if missing:
        return False, f"missing keys: {missing}"

    if not isinstance(result.get("debts"), list):
        return False, "debts is not a list"
    if not isinstance(result.get("goals"), list):
        return False, "goals is not a list"

    return True, ""


def run_matrix() -> None:
    agent_names = list(BUILDERS.keys())
    col_w = 11   # column width for agent names

    # Header
    print(f"\n{_BOLD}{'FinSight AI — Synthetic Data Agent Test Matrix (10×7 = 70 cases)'}{_RESET}")
    print("=" * (22 + col_w * len(agent_names)))

    # Column headers
    header = f"  {'User':<18} {'Health':<12}"
    for name in agent_names:
        header += f" {name:>{col_w}}"
    print(header)
    print("-" * len(header))

    total_pass = 0
    total_fail = 0
    failures: list[tuple[str, str, str, str]] = []   # (uid, name, builder, error)

    for user in SYNTHETIC_USERS:
        row_label = f"  {user['id']} {user['name']:<16} {user['financial_health']:<12}"
        row = row_label
        user_pass = 0
        user_fail = 0

        for bname, bfn in BUILDERS.items():
            passed, err = _check(user, bname, bfn)
            cell = f"{_GREEN}OK{_RESET}" if passed else f"{_RED}XX{_RESET}"
            row += f" {cell:>{col_w}}"

            if passed:
                user_pass += 1
                total_pass += 1
            else:
                user_fail += 1
                total_fail += 1
                failures.append((user["id"], user["name"], bname, err))

        status = f"{_GREEN}[{user_pass}/7]{_RESET}" if user_fail == 0 else f"{_RED}[{user_pass}/7]{_RESET}"
        print(row + f"  {status}")

    print("-" * len(header))

    # Totals row
    passed_str = f"{_GREEN}{total_pass} passed{_RESET}"
    failed_str = f"{_RED}{total_fail} failed{_RESET}" if total_fail else f"{_GREEN}0 failed{_RESET}"
    print(f"\n  Total: {passed_str} / {failed_str} out of 70 cases\n")

    # Financial invariant checks
    print(f"{_BOLD}Financial Invariant Checks:{_RESET}")
    _invariant("u04 negative surplus",   _check_invariant("u04", lambda u: u["_computed"]["monthly_surplus"] < 0))
    _invariant("u05 savings_rate < 5%",  _check_invariant("u05", lambda u: u["_computed"]["savings_rate"] < 0.05))
    _invariant("u09 EF < 1 month",       _check_invariant("u09", lambda u: u["_computed"]["emergency_fund_months"] < 1.0))
    _invariant("u10 savings_rate > 30%", _check_invariant("u10", lambda u: u["_computed"]["savings_rate"] > 0.30))
    print()

    # Print computed fields table
    print(f"{_BOLD}Computed Fields Table:{_RESET}")
    hdr2 = f"  {'ID':<4} {'Name':<18} {'Surplus/mo':>12} {'Sav.Rate':>10} {'Net Worth':>14} {'EF Months':>10}"
    print(hdr2)
    print("  " + "-" * (len(hdr2) - 2))
    for u in SYNTHETIC_USERS:
        c = u["_computed"]
        surplus_color = _RED if c["monthly_surplus"] < 0 else _GREEN
        sr_color      = _RED if c["savings_rate"] < 0.05 else (_GREEN if c["savings_rate"] > 0.30 else _RESET)
        ef_color      = _RED if c["emergency_fund_months"] < 1.0 else _RESET

        print(
            f"  {u['id']:<4} {u['name']:<18} "
            f"{surplus_color}{c['monthly_surplus']:>12.2f}{_RESET} "
            f"{sr_color}{c['savings_rate']:>10.4f}{_RESET} "
            f"{c['net_worth']:>14,.2f} "
            f"{ef_color}{c['emergency_fund_months']:>10.2f}{_RESET}"
        )
    print()

    # Failure details
    if failures:
        print(f"{_RED}{_BOLD}Failure Details:{_RESET}")
        for uid, name, builder, err in failures:
            print(f"  [{uid} {name}] builder='{builder}': {err}")
        print()
        sys.exit(1)
    else:
        print(f"{_GREEN}{_BOLD}All 70 cases passed.{_RESET}")


def _check_invariant(uid: str, predicate) -> bool:
    from data.synthetic_users import get_user_by_id
    user = get_user_by_id(uid)
    if user is None:
        return False
    return predicate(user)


def _invariant(label: str, passed: bool) -> None:
    status = f"{_GREEN}PASS{_RESET}" if passed else f"{_RED}FAIL{_RESET}"
    print(f"  {status}  {label}")


if __name__ == "__main__":
    run_matrix()
