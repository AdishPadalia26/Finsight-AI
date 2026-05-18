export type RiskTolerance = "conservative" | "moderate" | "aggressive";

export interface Debt {
  type: string;
  balance: number;
  monthly_payment: number;
  interest_rate: number;
}

export interface Goal {
  name: string;
  target_amount: number;
  target_years: number;
  priority: "high" | "medium" | "low";
}

export interface FinancialProfile {
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

export interface AnalyzeRequest {
  raw_input?: string;
  profile?: Record<string, unknown>;
  session_id?: string;
}

export type SSEEventType =
  | "pipeline_start"
  | "agent_start"
  | "agent_complete"
  | "revision_loop"
  | "pipeline_complete"
  | "pipeline_error";

export interface SSEEvent {
  event: SSEEventType;
  agent?: string;
  label?: string;
  status?: string;
  summary?: Record<string, unknown>;
  revision_number?: number;
  message?: string;
  final_report?: Record<string, unknown>;
  compliance_audit?: Record<string, unknown>;
  critic_scores?: Record<string, unknown>;
  pipeline_errors?: string[];
  session_id?: string;
  total_agents?: number;
  built_agents?: number;
}

export type AgentStatus = "idle" | "running" | "complete" | "error";

export interface AgentState {
  label: string;
  status: AgentStatus;
  summary?: Record<string, unknown>;
}

export type AnalysisStatus = "idle" | "running" | "complete" | "error";
