"""
Three pre-loaded demo personas for the live demo.
Load any of these instead of manual form entry during the presentation.
"""

ALEX = {
    "session_id": "demo-alex-001",
    "revision_count": 0,
    "pipeline_errors": None,
    "age": 27,
    "location": "Austin, TX",
    "monthly_income": 5500.0,
    "monthly_expenses": 4200.0,
    "savings": 8000.0,
    "investments": 3000.0,
    "property_value": 0.0,
    "debts": [
        {"type": "student_loan",  "balance": 28000.0, "interest_rate": 5.5,  "minimum_payment": 290.0},
        {"type": "credit_card",   "balance": 3200.0,  "interest_rate": 22.9, "minimum_payment": 85.0},
    ],
    "goals": [
        {"description": "Emergency fund (3 months expenses)", "target_amount": 16500.0,  "timeline_months": 18,  "priority": "critical"},
        {"description": "Buy a home (20% down payment)",      "target_amount": 60000.0,  "timeline_months": 48,  "priority": "high"},
    ],
    "risk_tolerance": "moderate",
    "investment_horizon": 35,
    "behavioral_fingerprint": None,
    "credit_score": None,
    "budget_recommendation": None,
    "goal_roadmap": None,
    "investment_strategy": None,
    "tax_opportunities": None,
    "debt_roadmap": None,
    "life_events": None,
    "critic_scores": None,
    "final_report": None,
    "compliance_audit": None,
}

JORDAN = {
    "session_id": "demo-jordan-001",
    "revision_count": 0,
    "pipeline_errors": None,
    "age": 42,
    "location": "Chicago, IL",
    "monthly_income": 12000.0,
    "monthly_expenses": 8500.0,
    "savings": 45000.0,
    "investments": 180000.0,
    "property_value": 420000.0,
    "debts": [
        {"type": "mortgage", "balance": 290000.0, "interest_rate": 3.75, "minimum_payment": 1850.0},
        {"type": "auto",     "balance": 18000.0,  "interest_rate": 6.9,  "minimum_payment": 380.0},
    ],
    "goals": [
        {"description": "Kids college fund",  "target_amount": 120000.0,  "timeline_months": 96,  "priority": "high"},
        {"description": "Retire at 60",       "target_amount": 2000000.0, "timeline_months": 216, "priority": "critical"},
    ],
    "risk_tolerance": "moderate",
    "investment_horizon": 18,
    "behavioral_fingerprint": None,
    "credit_score": None,
    "budget_recommendation": None,
    "goal_roadmap": None,
    "investment_strategy": None,
    "tax_opportunities": None,
    "debt_roadmap": None,
    "life_events": None,
    "critic_scores": None,
    "final_report": None,
    "compliance_audit": None,
}

SAM = {
    "session_id": "demo-sam-001",
    "revision_count": 0,
    "pipeline_errors": None,
    "age": 58,
    "location": "Seattle, WA",
    "monthly_income": 18000.0,
    "monthly_expenses": 9000.0,
    "savings": 120000.0,
    "investments": 680000.0,
    "property_value": 750000.0,
    "debts": [
        {"type": "mortgage", "balance": 85000.0, "interest_rate": 2.9, "minimum_payment": 720.0},
    ],
    "goals": [
        {"description": "Retire at 65",  "target_amount": 2500000.0, "timeline_months": 84, "priority": "critical"},
        {"description": "Travel fund",   "target_amount": 80000.0,   "timeline_months": 84, "priority": "medium"},
    ],
    "risk_tolerance": "conservative",
    "investment_horizon": 7,
    "behavioral_fingerprint": None,
    "credit_score": None,
    "budget_recommendation": None,
    "goal_roadmap": None,
    "investment_strategy": None,
    "tax_opportunities": None,
    "debt_roadmap": None,
    "life_events": None,
    "critic_scores": None,
    "final_report": None,
    "compliance_audit": None,
}

PERSONAS = {"alex": ALEX, "jordan": JORDAN, "sam": SAM}
