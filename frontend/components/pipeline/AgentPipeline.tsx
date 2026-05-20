"use client";

import { CheckCircle, Loader2, Lock, Minus, AlertCircle } from "lucide-react";
import type { AgentState } from "@/lib/types";

interface AgentDef {
  key: string;
  label: string;
  description: string;
  tier: 1 | 2 | 3;
  built: boolean;
}

const ALL_AGENTS: AgentDef[] = [
  {
    key: "profile_builder",
    label: "Profile Builder",
    description: "Validates input · Injection protection",
    tier: 1,
    built: true,
  },
  {
    key: "behavioral_pattern",
    label: "Behavioral Pattern",
    description: "Spending fingerprint analysis",
    tier: 1,
    built: true,
  },
  {
    key: "credit_intelligence",
    label: "Credit Intelligence",
    description: "Credit bureau · Score optimization",
    tier: 1,
    built: true,
  },
  {
    key: "budget_architect",
    label: "Budget Architect",
    description: "50/30/20 · Zero-based · Envelope",
    tier: 2,
    built: true,
  },
  {
    key: "goal_engineering",
    label: "Goal Engineering",
    description: "Goal feasibility · Milestone projections",
    tier: 2,
    built: true,
  },
  {
    key: "investment_strategist",
    label: "Investment Strategist",
    description: "Live market data · ETF allocation",
    tier: 2,
    built: true,
  },
  {
    key: "tax_intelligence",
    label: "Tax Intelligence",
    description: "2025 IRS limits · Bracket optimization",
    tier: 2,
    built: true,
  },
  {
    key: "debt_elimination",
    label: "Debt Elimination",
    description: "Avalanche · Snowball · Interest saved",
    tier: 2,
    built: true,
  },
  {
    key: "life_event",
    label: "Life Event Anticipation",
    description: "Proactive life change detection",
    tier: 3,
    built: true,
  },
  {
    key: "stress_test",
    label: "Stress Test Engine",
    description: "Job loss · Market crash · Rate spike",
    tier: 3,
    built: true,
  },
  {
    key: "personalised_advisor",
    label: "Personalised Advisor",
    description: "Cross-domain synthesis · 30-day plan",
    tier: 3,
    built: true,
  },
  {
    key: "critic",
    label: "Critic (Red Team)",
    description: "Adversarial review · Revision loop",
    tier: 3,
    built: true,
  },
  {
    key: "compliance",
    label: "Compliance Gate",
    description: "Regulatory scan · Disclaimer injection",
    tier: 3,
    built: true,
  },
  {
    key: "memory",
    label: "Memory Agent",
    description: "Longitudinal session learning",
    tier: 3,
    built: true,
  },
];

const TIER_CONFIG = {
  1: { label: "Tier 1 — Data Intelligence", border: "border-l-blue-500/40", header: "text-blue-400", bg: "bg-blue-500/5" },
  2: { label: "Tier 2 — Financial Planning", border: "border-l-amber-500/40", header: "text-amber-500", bg: "bg-amber-500/5" },
  3: { label: "Tier 3 — Intelligence & Safety", border: "border-l-cyan-400/40", header: "text-cyan-400", bg: "bg-cyan-500/5" },
} as const;

interface Props {
  agents: Record<string, AgentState>;
  revisionCount?: number;
}

function StatusDot({ status, built }: { status: string; built: boolean }) {
  if (!built) {
    return (
      <div className="w-6 h-6 rounded-full border border-gray-700 flex items-center justify-center shrink-0">
        <Lock size={10} className="text-gray-600" />
      </div>
    );
  }
  if (status === "running") {
    return (
      <div className="w-6 h-6 rounded-full border-2 border-amber-500 flex items-center justify-center shrink-0 animate-agent-glow">
        <Loader2 size={12} className="text-amber-500 animate-spin" />
      </div>
    );
  }
  if (status === "complete") {
    return (
      <div className="w-6 h-6 rounded-full bg-cyan-400/10 border border-cyan-400/40 flex items-center justify-center shrink-0">
        <CheckCircle size={12} className="text-cyan-400" />
      </div>
    );
  }
  if (status === "error") {
    return (
      <div className="w-6 h-6 rounded-full bg-red-500/10 border border-red-500/40 flex items-center justify-center shrink-0">
        <AlertCircle size={12} className="text-red-400" />
      </div>
    );
  }
  return (
    <div className="w-6 h-6 rounded-full border border-gray-700 flex items-center justify-center shrink-0">
      <Minus size={10} className="text-gray-700" />
    </div>
  );
}

function AgentRow({ agent, state }: { agent: AgentDef; state?: AgentState }) {
  const status = state?.status ?? "idle";
  const isRunning = status === "running";
  const isComplete = status === "complete";
  const tier = TIER_CONFIG[agent.tier];

  const summaryEntries = state?.summary
    ? Object.entries(state.summary).filter(([, v]) => v != null && typeof v !== "object").slice(0, 3)
    : [];

  return (
    <div
      className={`flex items-start gap-3 rounded-xl px-3 py-2.5 border-l-2 transition-all ${
        isRunning
          ? "border-l-amber-500/40 bg-amber-500/5 border border-r-0 border-t-0 border-b-0"
          : isComplete
          ? `${tier.border} border border-r-0 border-t-0 border-b-0 border-gray-800/40`
          : "border-gray-800/0 border border-r-0 border-t-0 border-b-0"
      }`}
    >
      <div className="mt-0.5">
        <StatusDot status={status} built={agent.built} />
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span
            className={`text-xs font-semibold font-ui ${
            isRunning ? "text-white" : isComplete ? "text-gray-200" : "text-gray-400"
            } ${!agent.built ? "text-slate-600" : ""
            }`}
          >
            {agent.label}
          </span>
          {isRunning && (
            <span className="text-[9px] font-jet text-amber-400 animate-pulse">
              running…
            </span>
          )}
        </div>
        <p className="text-[10px] text-gray-600 mt-0.5 font-ui">{agent.description}</p>
        {isComplete && summaryEntries.length > 0 && (
          <div className="animate-slide-down mt-2 flex flex-wrap gap-1.5">
            {summaryEntries.map(([key, value]) => (
              <span
                key={key}
                className="max-w-full truncate rounded-full border border-amber-500/15 bg-amber-500/8 px-2 py-0.5 text-[9px] font-jet text-amber-300/90"
              >
                {key.replace(/_/g, " ")}: {String(value)}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function AgentPipeline({ agents, revisionCount = 0 }: Props) {
  const completedCount = ALL_AGENTS.filter(
    (a) => agents[a.key]?.status === "complete"
  ).length;

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <h2 className="text-sm font-semibold text-white font-ui">Agent Pipeline</h2>
          <div className="text-[10px] font-jet text-gray-600">
            {completedCount}/{ALL_AGENTS.length} agents
          </div>
        </div>
        {revisionCount > 0 && (
          <span className="text-[10px] font-jet text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-full px-3 py-1">
            REVISION #{revisionCount}
          </span>
        )}
      </div>

      <div className="p-4 space-y-5">
        {([1, 2, 3] as const).map((tier) => {
          const config = TIER_CONFIG[tier];
          const tierAgents = ALL_AGENTS.filter((a) => a.tier === tier);
          const tierRunning = tierAgents.some(
            (a) => agents[a.key]?.status === "running"
          );

          return (
            <div key={tier} className="relative pl-4">
              {tier < 3 && (
                <div className="absolute left-0 top-8 h-[calc(100%+1.25rem)] border-l border-dashed border-slate-700" />
              )}
              <div className="flex items-center gap-2 mb-2">
                <p
                  className={`text-[10px] font-jet tracking-widest ${config.header}`}
                >
                  {config.label.toUpperCase()}
                </p>
                {tierRunning && (
                  <span className="w-1 h-1 rounded-full bg-amber-500 animate-pulse" />
                )}
              </div>
              <div className="space-y-1">
                {tierAgents.map((agent) => (
                  <AgentRow
                    key={agent.key}
                    agent={agent}
                    state={agents[agent.key]}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
