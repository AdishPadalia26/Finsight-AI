"""
Print a formatted summary table of all 10 synthetic users.

    python -m data.synthetic_users_summary
"""

from data.synthetic_users import SYNTHETIC_USERS

_HEALTH_COLOR = {
    "distressed": "\033[91m",   # red
    "struggling":  "\033[93m",  # yellow
    "stable":      "\033[94m",  # blue
    "thriving":    "\033[92m",  # green
}
_RESET = "\033[0m"

_RISK_SYMBOL = {
    "conservative": "▼",
    "moderate":     "●",
    "aggressive":   "▲",
}


def _fmt_currency(v: float) -> str:
    if abs(v) >= 1_000_000:
        return f"${v/1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"${v/1_000:.0f}K"
    return f"${v:.0f}"


def _fmt_pct(v: float) -> str:
    return f"{v*100:.1f}%"


def print_summary(use_color: bool = True) -> None:
    col = _HEALTH_COLOR if use_color else {}
    reset = _RESET if use_color else ""

    header = (
        f"{'#':<4} {'Name':<18} {'Age':>4} {'Location':<18} "
        f"{'Income/mo':>10} {'Surplus/mo':>11} {'Sav.Rate':>9} "
        f"{'Net Worth':>10} {'EF Months':>10} {'Health':<12} {'Risk':<6}"
    )
    sep = "-" * len(header)

    print(sep)
    print("  FinSight AI — Synthetic User Profiles")
    print(sep)
    print(header)
    print(sep)

    for u in SYNTHETIC_USERS:
        c = u["_computed"]
        health = u["financial_health"]
        color = col.get(health, "")
        risk_sym = _RISK_SYMBOL.get(u["risk_tolerance"], "?")

        surplus_str = _fmt_currency(c["monthly_surplus"])
        if c["monthly_surplus"] < 0:
            surplus_str = f"-${abs(c['monthly_surplus'])/1_000:.1f}K" if abs(c['monthly_surplus']) >= 1000 else f"-${abs(c['monthly_surplus']):.0f}"

        row = (
            f"{u['id']:<4} {u['name']:<18} {u['age']:>4} {u['location']:<18} "
            f"{_fmt_currency(u['monthly_income']):>10} {surplus_str:>11} "
            f"{_fmt_pct(c['savings_rate']):>9} "
            f"{_fmt_currency(c['net_worth']):>10} "
            f"{c['emergency_fund_months']:>10.2f} "
            f"{color}{health:<12}{reset} {risk_sym} {u['risk_tolerance']}"
        )
        print(row)

    print(sep)

    # Distribution summary
    print("\nDistribution:")
    from collections import Counter
    health_dist  = Counter(u["financial_health"] for u in SYNTHETIC_USERS)
    stage_dist   = Counter(u["life_stage"]       for u in SYNTHETIC_USERS)
    risk_dist    = Counter(u["risk_tolerance"]   for u in SYNTHETIC_USERS)

    print(f"  Health:  {dict(health_dist)}")
    print(f"  Stage:   {dict(stage_dist)}")
    print(f"  Risk:    {dict(risk_dist)}")

    # Special invariants
    neg_surplus = [u["id"] for u in SYNTHETIC_USERS if u["_computed"]["monthly_surplus"] < 0]
    low_ef      = [u["id"] for u in SYNTHETIC_USERS if u["_computed"]["emergency_fund_months"] < 1.0]
    low_sr      = [u["id"] for u in SYNTHETIC_USERS if u["_computed"]["savings_rate"] < 0.05]
    high_sr     = [u["id"] for u in SYNTHETIC_USERS if u["_computed"]["savings_rate"] > 0.30]

    print(f"\n  Negative surplus:         {neg_surplus}")
    print(f"  EF < 1 month:             {low_ef}")
    print(f"  Savings rate < 5%:        {low_sr}")
    print(f"  Savings rate > 30%:       {high_sr}")
    print()


if __name__ == "__main__":
    print_summary()
