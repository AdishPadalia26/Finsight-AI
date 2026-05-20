"""
FinSight AI — LangGraph State Machine

Execution flow:
  Step 1  Sequential   : profile_builder
  Step 2  Parallel T1  : behavioral_pattern + credit_intelligence
  Step 3  Sequential   : tier1_join → tier2_entry
  Step 4  Parallel T2  : budget_architect + goal_engineering + investment_strategist
                         + tax_intelligence + debt_elimination
  Step 5  Sequential   : tier2_join → life_event → stress_test → personalised_advisor
  Step 6  Sequential   : → critic
  Step 7  Conditional  : critic ──► revise → tier2_entry (max 3 loops)
                               └──► approve → compliance
  Step 8  Sequential   : compliance → final_report_assembler → memory → END
"""

from datetime import datetime, timezone
from typing import Literal
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from graph.state import FinancialProfile
from agents.tier1.profile_builder import ProfileBuilderAgent
from agents.tier1.behavioral_pattern import BehavioralPatternAgent
from agents.tier1.credit_intelligence import CreditIntelligenceAgent
from agents.tier2.budget_architect import BudgetArchitectAgent
from agents.tier2.goal_engineering import GoalEngineeringAgent
from agents.tier2.investment_strategist import InvestmentStrategistAgent
from agents.tier2.tax_intelligence import TaxIntelligenceAgent
from agents.tier2.debt_elimination import DebtEliminationAgent
from agents.tier3.life_event_agent import LifeEventAgent
from agents.tier3.personalised_advisor import PersonalisedAdvisorAgent
from agents.tier3.critic_agent import CriticAgent
from agents.tier3.compliance_agent import ComplianceAgent
from agents.tier3.memory_agent import MemoryAgent
from tools.financial.calculator import (
    compute_stress_tests,
    savings_rate, debt_to_income, emergency_fund_months,
    net_worth, total_minimum_debt_payments, total_debt_balance,
    financial_health_score,
)

load_dotenv()

_STATE_KEYS = set(FinancialProfile.__annotations__)

# ── Singleton agents — instantiated once, reused across all requests ──────────
_AGENTS = {
    "profile_builder":       ProfileBuilderAgent(),
    "behavioral_pattern":    BehavioralPatternAgent(),
    "credit_intelligence":   CreditIntelligenceAgent(),
    "budget_architect":      BudgetArchitectAgent(),
    "goal_engineering":      GoalEngineeringAgent(),
    "investment_strategist": InvestmentStrategistAgent(),
    "tax_intelligence":      TaxIntelligenceAgent(),
    "debt_elimination":      DebtEliminationAgent(),
    "life_event":            LifeEventAgent(),
    "personalised_advisor":  PersonalisedAdvisorAgent(),
    "critic":                CriticAgent(),
    "compliance":            ComplianceAgent(),
    "memory":                MemoryAgent(),
}


# ── Error handling wrapper ────────────────────────────────────────────────────

def _fallback_investment_strategy(state: FinancialProfile, reason: str = "Investment strategist unavailable.") -> dict:
    risk = state.get("risk_tolerance") or "moderate"
    if risk == "conservative":
        allocation = {
            "us_equities": 35,
            "international_equities": 15,
            "bonds": 35,
            "cash": 10,
            "alternatives": 5,
        }
    elif risk == "aggressive":
        allocation = {
            "us_equities": 60,
            "international_equities": 25,
            "bonds": 10,
            "cash": 2,
            "alternatives": 3,
        }
    else:
        allocation = {
            "us_equities": 50,
            "international_equities": 20,
            "bonds": 20,
            "cash": 5,
            "alternatives": 5,
        }

    return {
        "allocation": allocation,
        "risk_alignment": (
            f"Fallback allocation reflects a {risk} profile and "
            f"{state.get('investment_horizon', 0)} year horizon. "
            "Past performance does not guarantee future results."
        ),
        "etf_categories": {
            "us_equities": "broad US equity index funds",
            "international_equities": "broad international equity index funds",
            "bonds": "investment-grade bond funds",
            "cash": "high-liquidity cash equivalents",
            "alternatives": "diversifying real-asset or alternative strategy funds",
        },
        "account_optimization": (
            "Use tax-advantaged retirement accounts for higher-growth and income-producing assets "
            "when available; keep cash needs liquid and taxable holdings tax-efficient."
        ),
        "rebalancing_guidance": "Review quarterly and rebalance when any asset class drifts more than 5 percentage points.",
        "rationale": reason,
        "market_context": {},
        "live_market_snapshot": {},
        "fallback": True,
    }


def _state_delta(before: FinancialProfile, after: dict) -> dict:
    return {
        key: value
        for key, value in after.items()
        if key in _STATE_KEYS and before.get(key) != value
    }


def _safe_run(agent_key: str, state: FinancialProfile) -> dict:
    try:
        return _state_delta(state, _AGENTS[agent_key].run(state))
    except Exception as e:
        error = f"[{agent_key}] {type(e).__name__}: {str(e)[:300]}"
        if agent_key == "investment_strategist":
            return {
                "investment_strategy": _fallback_investment_strategy(state, error),
                "pipeline_errors": [error],
            }
        return {"pipeline_errors": [error]}


# ── Node functions ────────────────────────────────────────────────────────────

# Tier 1 — Data Intelligence

def node_profile_builder(state: FinancialProfile) -> FinancialProfile:
    if not state.get("raw_input") and state.get("monthly_income") is not None:
        return {}
    return _AGENTS["profile_builder"].run(state)

def node_behavioral_pattern(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("behavioral_pattern", state)

def node_credit_intelligence(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("credit_intelligence", state)

def node_tier1_join(state: FinancialProfile) -> FinancialProfile:
    return {}


# Tier 2 — Financial Planning

def node_tier2_entry(state: FinancialProfile) -> FinancialProfile:
    revision_count = state.get("revision_count", 0)
    if state.get("critic_scores") is not None:
        revision_count += 1
    return {"revision_count": revision_count}

def node_budget_architect(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("budget_architect", state)

def node_goal_engineering(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("goal_engineering", state)

def node_investment_strategist(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("investment_strategist", state)

def node_tax_intelligence(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("tax_intelligence", state)

def node_debt_elimination(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("debt_elimination", state)

def node_tier2_join(state: FinancialProfile) -> FinancialProfile:
    return {}


# Tier 3 — Intelligence & Safety

def node_life_event(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("life_event", state)


def node_stress_test(state: FinancialProfile) -> FinancialProfile:
    """Deterministic stress-test computation — no LLM needed."""
    try:
        result = compute_stress_tests(
            monthly_income=state.get("monthly_income", 0),
            monthly_expenses=state.get("monthly_expenses", 0),
            savings=state.get("savings", 0),
            investments=state.get("investments", 0),
            debts=state.get("debts", []),
        )
        return {"stress_tests": result}
    except Exception as e:
        return {"pipeline_errors": [f"[stress_test] {type(e).__name__}: {str(e)[:200]}"]}


def node_personalised_advisor(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("personalised_advisor", state)


def node_critic(state: FinancialProfile) -> FinancialProfile:
    try:
        return _state_delta(state, _AGENTS["critic"].run(state))
    except Exception as e:
        return {
            "critic_scores": {
                "status": "ACCEPTED_WITH_CAVEATS",
                "note": "Critic LLM unavailable; accepted with caveats for demo continuity.",
                "error": f"{type(e).__name__}: {str(e)[:200]}",
                "revision_count": state.get("revision_count", 0),
            }
        }

def node_compliance(state: FinancialProfile) -> FinancialProfile:
    return _state_delta(state, _AGENTS["compliance"].run(state))

def node_memory(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("memory", state)


def node_final_report_assembler(state: FinancialProfile) -> FinancialProfile:
    """Builds the canonical final_report schema from all state fields."""
    income = state.get("monthly_income", 0)
    expenses = state.get("monthly_expenses", 0)
    savings = state.get("savings", 0)
    investments = state.get("investments", 0)
    property_value = state.get("property_value", 0)
    debts = state.get("debts", [])

    min_debt = total_minimum_debt_payments(debts)
    total_debt = total_debt_balance(debts)
    # True surplus and savings rate include debt minimum payments as outflow
    monthly_surplus = round(income - expenses - min_debt, 2)
    sr = savings_rate(income, expenses + min_debt)
    dti = debt_to_income(min_debt, income)
    em = emergency_fund_months(savings, expenses)
    nw = net_worth(savings, investments, property_value, total_debt)
    health = financial_health_score(sr, dti, em)

    report = {
        "session": {
            "session_id": state.get("session_id"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "location": state.get("location"),
            "age": state.get("age"),
            "risk_tolerance": state.get("risk_tolerance"),
            "investment_horizon_years": state.get("investment_horizon"),
        },
        "overview": {
            "health_score": health["total"],
            "health_grade": health["grade"],
            "savings_score": health["savings_score"],
            "dti_score": health["dti_score"],
            "emergency_score": health["emergency_score"],
            "monthly_income": income,
            "monthly_expenses": expenses,
            "monthly_debt_payments": round(min_debt, 2),
            "monthly_surplus": monthly_surplus,
            "savings_rate": sr,
            "debt_to_income": dti,
            "emergency_fund_months": em,
            "net_worth": nw,
            "total_debt": total_debt,
        },
        "behavioral_fingerprint": state.get("behavioral_fingerprint"),
        "budget": state.get("budget_recommendation"),
        "investment": state.get("investment_strategy") or _fallback_investment_strategy(
            state,
            "Investment strategy was missing at report assembly; deterministic fallback shown.",
        ),
        "goals": state.get("goal_roadmap"),
        "debt": state.get("debt_roadmap"),
        "tax": state.get("tax_opportunities"),
        "life_events": state.get("life_events"),
        "stress_tests": state.get("stress_tests"),
        "personalised_advice": state.get("personalised_advice"),
        "critic": state.get("critic_scores"),
        "compliance": state.get("compliance_audit"),
    }

    return {"final_report": report}


# ── Conditional routing: Critic revision loop ─────────────────────────────────

def route_after_critic(state: FinancialProfile) -> Literal["revise", "approve"]:
    critic = state.get("critic_scores") or {}
    revision_count = state.get("revision_count", 0)
    if critic.get("status") == "NEEDS_REVISION" and revision_count < 3:
        return "revise"
    return "approve"


# ── Graph construction ────────────────────────────────────────────────────────

def build_graph():
    """
    Builds and compiles the full FinSight AI LangGraph state machine.
    """
    g = StateGraph(FinancialProfile)

    # ── Register all nodes ─────────────────────────────────────────────────
    g.add_node("profile_builder",         node_profile_builder)
    g.add_node("behavioral_pattern",      node_behavioral_pattern)
    g.add_node("credit_intelligence",     node_credit_intelligence)
    g.add_node("tier1_join",              node_tier1_join)
    g.add_node("tier2_entry",             node_tier2_entry)
    g.add_node("budget_architect",        node_budget_architect)
    g.add_node("goal_engineering",        node_goal_engineering)
    g.add_node("investment_strategist",   node_investment_strategist)
    g.add_node("tax_intelligence",        node_tax_intelligence)
    g.add_node("debt_elimination",        node_debt_elimination)
    g.add_node("tier2_join",              node_tier2_join)
    g.add_node("life_event",              node_life_event)
    g.add_node("stress_test",             node_stress_test)
    g.add_node("personalised_advisor",    node_personalised_advisor)
    g.add_node("critic",                  node_critic)
    g.add_node("compliance",              node_compliance)
    g.add_node("final_report_assembler",  node_final_report_assembler)
    g.add_node("memory",                  node_memory)

    # ── Step 1: Entry ─────────────────────────────────────────────────────
    g.set_entry_point("profile_builder")

    # ── Step 2: Tier 1 parallel fan-out ──────────────────────────────────
    g.add_edge("profile_builder", "behavioral_pattern")
    g.add_edge("profile_builder", "credit_intelligence")
    g.add_edge("behavioral_pattern",  "tier1_join")
    g.add_edge("credit_intelligence", "tier1_join")
    g.add_edge("tier1_join", "tier2_entry")

    # ── Step 3: Tier 2 parallel fan-out ──────────────────────────────────
    g.add_edge("tier2_entry", "budget_architect")
    g.add_edge("tier2_entry", "goal_engineering")
    g.add_edge("tier2_entry", "investment_strategist")
    g.add_edge("tier2_entry", "tax_intelligence")
    g.add_edge("tier2_entry", "debt_elimination")

    # ── Step 4: Tier 2 join ───────────────────────────────────────────────
    g.add_edge("budget_architect",      "tier2_join")
    g.add_edge("goal_engineering",      "tier2_join")
    g.add_edge("investment_strategist", "tier2_join")
    g.add_edge("tax_intelligence",      "tier2_join")
    g.add_edge("debt_elimination",      "tier2_join")

    # ── Step 5: Sequential synthesis layer ───────────────────────────────
    g.add_edge("tier2_join",           "life_event")
    g.add_edge("life_event",           "stress_test")
    g.add_edge("stress_test",          "personalised_advisor")
    g.add_edge("personalised_advisor", "critic")

    # ── Step 6: Critic revision loop ──────────────────────────────────────
    g.add_conditional_edges(
        "critic",
        route_after_critic,
        {"revise": "tier2_entry", "approve": "compliance"},
    )

    # ── Step 7: Final output ──────────────────────────────────────────────
    g.add_edge("compliance",            "final_report_assembler")
    g.add_edge("final_report_assembler", "memory")
    g.add_edge("memory",                END)

    return g.compile()


# ── Module-level compiled graph ───────────────────────────────────────────────
app = build_graph()
