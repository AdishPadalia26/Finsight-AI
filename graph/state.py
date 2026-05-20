from typing import Annotated, TypedDict, Optional, List


def merge_pipeline_errors(left: Optional[List[str]], right: Optional[List[str]]) -> List[str]:
    """Append pipeline errors from parallel graph branches."""
    return list(left or []) + list(right or [])


class Debt(TypedDict):
    type: str           # "credit_card", "student_loan", "mortgage", "auto", "bnpl"
    balance: float
    interest_rate: float
    minimum_payment: float


class Goal(TypedDict):
    description: str
    target_amount: float
    timeline_months: int
    priority: str       # "critical", "high", "medium", "low"


class FinancialProfile(TypedDict):
    # Pipeline entry
    raw_input: Optional[str]        # raw text from user — consumed by Profile Builder only

    # Session tracking
    session_id: str
    revision_count: int             # tracks Critic Agent revision loop iterations
    pipeline_errors: Annotated[Optional[List[str]], merge_pipeline_errors]

    # Demographics
    age: int
    location: str

    # Income & expenses
    monthly_income: float
    monthly_expenses: float

    # Assets
    savings: float
    investments: float
    property_value: float

    # Debts
    debts: List[Debt]

    # Goals
    goals: List[Goal]

    # Risk & preferences
    risk_tolerance: str             # "conservative", "moderate", "aggressive"
    investment_horizon: int         # years

    # Optional user-provided hints (improves agent accuracy)
    employment_status: Optional[str]   # "full_time", "part_time", "self_employed", "student", "retired", "unemployed"
    tax_bracket: Optional[float]       # marginal federal bracket as decimal, e.g. 0.22 for 22%
    recent_life_events: Optional[list] # ["new_job", "had_child", "job_loss", "marriage", ...] — informs LifeEventAgent

    # Filled progressively by agents
    behavioral_fingerprint: Optional[dict]
    credit_score: Optional[int]
    budget_recommendation: Optional[dict]
    goal_roadmap: Optional[dict]
    investment_strategy: Optional[dict]
    tax_opportunities: Optional[dict]
    debt_roadmap: Optional[dict]
    life_events: Optional[dict]
    stress_tests: Optional[dict]
    personalised_advice: Optional[dict]
    critic_scores: Optional[dict]
    final_report: Optional[dict]
    compliance_audit: Optional[dict]
