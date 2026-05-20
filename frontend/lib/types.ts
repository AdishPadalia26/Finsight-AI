export type RiskTolerance = "conservative" | "moderate" | "aggressive";

export interface Debt {
  type: string;
  balance: number;
  interest_rate: number;
  minimum_payment: number;
}

export interface Goal {
  description: string;
  target_amount: number;
  timeline_months: number;
  priority: "critical" | "high" | "medium" | "low";
}

export interface FinancialProfile {
  age: number;
  location: string;
  employment_status?: string;
  monthly_income: number;
  monthly_expenses: number;
  savings: number;
  investments: number;
  property_value: number;
  debts: Debt[];
  goals: Goal[];
  risk_tolerance: RiskTolerance;
  investment_horizon: number;
  credit_score?: number;
  tax_bracket?: number;           // marginal federal bracket as decimal, e.g. 0.22
  recent_life_events?: string[];  // ["new_job", "had_child", ...]
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
