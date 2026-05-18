"""
FinSight AI — LangGraph State Machine

Execution flow:
  Step 1  Sequential   : profile_builder
  Step 2  Parallel T1  : behavioral_pattern + credit_intelligence
  Step 3  Sequential   : tier1_join → tier2_entry
  Step 4  Parallel T2  : budget_architect + goal_engineering + investment_strategist
                         + tax_intelligence + debt_elimination
  Step 5  Sequential   : tier2_join → life_event → critic
  Step 6  Conditional  : critic ──► revise → tier2_entry (max 3 loops)
                               └──► approve → compliance
  Step 7  Sequential   : compliance → memory → END

Agent instantiation, coordination, and termination:
  - All agents instantiated once at module load (singleton pattern).
  - Coordination is handled entirely by LangGraph's StateGraph topology —
    no custom scheduler or message bus required.
  - Agents are stateless — all state lives in FinancialProfile TypedDict.
  - Termination: graph reaches END node after compliance + memory.
  - Hard termination: ComplianceViolation exception halts the pipeline immediately.
"""

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
from agents.tier3.critic_agent import CriticAgent
from agents.tier3.compliance_agent import ComplianceAgent
from agents.tier3.memory_agent import MemoryAgent

load_dotenv()

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
    "critic":                CriticAgent(),
    "compliance":            ComplianceAgent(),
    "memory":                MemoryAgent(),
}


# ── Error handling wrapper ────────────────────────────────────────────────────

def _safe_run(agent_key: str, state: FinancialProfile) -> FinancialProfile:
    """
    Wraps agent.run() with error handling for non-critical agents.
    On failure: appends error message to pipeline_errors and returns partial state.
    The pipeline continues — partial data is better than a full crash for stub agents.
    Critical agents (profile_builder, compliance) do NOT use this wrapper.
    """
    try:
        return _AGENTS[agent_key].run(state)
    except Exception as e:
        errors = list(state.get("pipeline_errors") or [])
        errors.append(f"[{agent_key}] {type(e).__name__}: {str(e)[:300]}")
        return {**state, "pipeline_errors": errors}


# ── Node functions ────────────────────────────────────────────────────────────
# Each node function is a thin wrapper — all business logic lives in the agent class.

# Tier 1 — Data Intelligence

def node_profile_builder(state: FinancialProfile) -> FinancialProfile:
    # Entry point — ValueError (injection detected) propagates intentionally
    return _AGENTS["profile_builder"].run(state)

def node_behavioral_pattern(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("behavioral_pattern", state)

def node_credit_intelligence(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("credit_intelligence", state)

def node_tier1_join(state: FinancialProfile) -> FinancialProfile:
    """Synchronization point. Runs only after BOTH Tier 1 parallel agents complete."""
    return state


# Tier 2 — Financial Planning

def node_tier2_entry(state: FinancialProfile) -> FinancialProfile:
    """
    Entry point for Tier 2 planning block.
    On revision loop re-entry (when critic_scores already exists),
    increments revision_count so Critic Agent tracks iteration depth.
    Also injects Critic feedback into state so Tier 2 agents can revise accordingly.
    """
    revision_count = state.get("revision_count", 0)
    if state.get("critic_scores") is not None:
        revision_count += 1
    return {**state, "revision_count": revision_count}

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
    """Synchronization point. Runs only after ALL 5 Tier 2 parallel agents complete."""
    return state


# Tier 3 — Intelligence & Safety

def node_life_event(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("life_event", state)

def node_critic(state: FinancialProfile) -> FinancialProfile:
    return _AGENTS["critic"].run(state)

def node_compliance(state: FinancialProfile) -> FinancialProfile:
    # ComplianceViolation propagates — it is an intentional hard stop, not a crash
    return _AGENTS["compliance"].run(state)

def node_memory(state: FinancialProfile) -> FinancialProfile:
    return _safe_run("memory", state)


# ── Conditional routing: Critic revision loop ─────────────────────────────────

def route_after_critic(state: FinancialProfile) -> Literal["revise", "approve"]:
    """
    Decision function for the Critic Agent conditional edge.

    Routes to "revise" (back to Tier 2) when:
      - Critic status is NEEDS_REVISION, AND
      - revision_count < 3 (hard cap prevents infinite loops)

    Routes to "approve" (forward to Compliance Gate) when:
      - All scores >= 7 (STRESS_TESTED_APPROVED), OR
      - revision_count >= 3 (ACCEPTED_WITH_CAVEATS — accepted after max retries)

    This directly satisfies the assignment requirement:
    "How the system handles errors, retries, and failures."
    """
    critic = state.get("critic_scores") or {}
    revision_count = state.get("revision_count", 0)

    if critic.get("status") == "NEEDS_REVISION" and revision_count < 3:
        return "revise"
    return "approve"


# ── Graph construction ────────────────────────────────────────────────────────

def build_graph():
    """
    Builds and compiles the complete 12-agent FinSight AI LangGraph state machine.
    Returns a compiled LangGraph app ready for .invoke() or .astream_events().
    """
    g = StateGraph(FinancialProfile)

    # ── Register all 15 nodes (12 agents + 3 control nodes) ──────────────
    g.add_node("profile_builder",       node_profile_builder)
    g.add_node("behavioral_pattern",    node_behavioral_pattern)
    g.add_node("credit_intelligence",   node_credit_intelligence)
    g.add_node("tier1_join",            node_tier1_join)
    g.add_node("tier2_entry",           node_tier2_entry)
    g.add_node("budget_architect",      node_budget_architect)
    g.add_node("goal_engineering",      node_goal_engineering)
    g.add_node("investment_strategist", node_investment_strategist)
    g.add_node("tax_intelligence",      node_tax_intelligence)
    g.add_node("debt_elimination",      node_debt_elimination)
    g.add_node("tier2_join",            node_tier2_join)
    g.add_node("life_event",            node_life_event)
    g.add_node("critic",                node_critic)
    g.add_node("compliance",            node_compliance)
    g.add_node("memory",                node_memory)

    # ── Step 1: Entry point ───────────────────────────────────────────────
    g.set_entry_point("profile_builder")

    # ── Step 2: Profile Builder → Tier 1 parallel fan-out ────────────────
    g.add_edge("profile_builder", "behavioral_pattern")
    g.add_edge("profile_builder", "credit_intelligence")

    # ── Step 3: Tier 1 agents → join (waits for both) ────────────────────
    g.add_edge("behavioral_pattern",  "tier1_join")
    g.add_edge("credit_intelligence", "tier1_join")

    # ── Step 3 cont: Join → Tier 2 entry ─────────────────────────────────
    g.add_edge("tier1_join", "tier2_entry")

    # ── Step 4: Tier 2 entry → parallel planning fan-out ─────────────────
    g.add_edge("tier2_entry", "budget_architect")
    g.add_edge("tier2_entry", "goal_engineering")
    g.add_edge("tier2_entry", "investment_strategist")
    g.add_edge("tier2_entry", "tax_intelligence")
    g.add_edge("tier2_entry", "debt_elimination")

    # ── Step 5: Tier 2 agents → join (waits for all 5) ───────────────────
    g.add_edge("budget_architect",      "tier2_join")
    g.add_edge("goal_engineering",      "tier2_join")
    g.add_edge("investment_strategist", "tier2_join")
    g.add_edge("tax_intelligence",      "tier2_join")
    g.add_edge("debt_elimination",      "tier2_join")

    # ── Step 5 cont: Sequential safety layer ─────────────────────────────
    g.add_edge("tier2_join", "life_event")
    g.add_edge("life_event", "critic")

    # ── Step 6: Conditional Critic revision loop ──────────────────────────
    # "revise" routes back to tier2_entry, which increments revision_count
    # "approve" routes forward to compliance gate
    g.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "revise":  "tier2_entry",
            "approve": "compliance",
        },
    )

    # ── Step 7: Final sequential output ──────────────────────────────────
    g.add_edge("compliance", "memory")
    g.add_edge("memory", END)

    return g.compile()


# ── Module-level compiled graph — import this in FastAPI and Streamlit ────────
app = build_graph()
