export type RiskTolerance = "conservative" | "moderate" | "aggressive";
export type GoalPriority = "critical" | "high" | "medium" | "low";
export type DebtType = "credit_card" | "student_loan" | "mortgage" | "auto" | "bnpl";
export type AgentTier = 1 | 2 | 3;
export type AgentStatusNew = "waiting" | "running" | "complete" | "error" | "stub";

export interface Debt {
  type: DebtType;
  balance: number;
  interest_rate: number;
  minimum_payment: number;
}

export interface Goal {
  description: string;
  target_amount: number;
  timeline_months: number;
  priority: GoalPriority;
}

export interface FinancialProfileNew {
  age: number;
  location: string;
  monthly_income: number;
  monthly_expenses: number;
  savings: number;
  investments: number;
  property_value: number;
  debts: Debt[];
  goals: Goal[];
  risk_tolerance: RiskTolerance;
  investment_horizon: number;
}

export interface AgentInfo {
  id: string;
  displayName: string;
  tier: AgentTier;
  description: string;
  isStub: boolean;
}

export interface BudgetCategory {
  name: string;
  current: number;
  recommended: number;
  status: "over" | "under" | "good";
}

export interface AllocationItem {
  asset_class: string;
  percentage: number;
  description: string;
}

export interface MarketContext {
  fed_funds_rate: number;
  cpi_rate: number;
  treasury_10yr: number;
  sp500_ytd: number;
  data_timestamp: string;
}

export interface StressTestResult {
  scenario: string;
  description: string;
  resilience_score: number;
  vulnerabilities: string[];
  recommendations: string[];
}

export interface DemoPersona {
  id: "alex" | "jordan" | "sam";
  name: string;
  age: number;
  tagline: string;
  income: string;
}
