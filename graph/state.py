from typing import TypedDict, Optional, List


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
    # Session tracking
    session_id: str
    revision_count: int             # tracks Critic Agent revision loop iterations
    pipeline_errors: Optional[List[str]]

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

    # Filled progressively by agents
    behavioral_fingerprint: Optional[dict]
    credit_score: Optional[int]
    budget_recommendation: Optional[dict]
    goal_roadmap: Optional[dict]
    investment_strategy: Optional[dict]
    tax_opportunities: Optional[dict]
    debt_roadmap: Optional[dict]
    life_events: Optional[list]
    critic_scores: Optional[dict]
    final_report: Optional[dict]
    compliance_audit: Optional[dict]
