"use client";

import type { AgentState } from "@/lib/types";

const ALL_AGENTS = [
  { key: "profile_builder",       label: "Profile Builder",            tier: 1, built: true },
  { key: "behavioral_pattern",    label: "Behavioral Pattern",         tier: 1, built: true },
  { key: "credit_intelligence",   label: "Credit Intelligence",        tier: 1, built: true },
  { key: "budget_architect",      label: "Budget Architect",           tier: 2, built: true },
  { key: "goal_engineering",      label: "Goal Engineering",           tier: 2, built: true },
  { key: "investment_strategist", label: "Investment Strategist",      tier: 2, built: true },
  { key: "tax_intelligence",      label: "Tax Intelligence",           tier: 2, built: true },
  { key: "debt_elimination",      label: "Debt Elimination",           tier: 2, built: true },
  { key: "life_event",            label: "Life Event Anticipation",    tier: 3, built: true },
  { key: "personalised_advisor",  label: "Personalised Advisor",       tier: 3, built: true },
  { key: "critic",                label: "Critic / Red Team",          tier: 3, built: true },
  { key: "compliance",            label: "Compliance Gate",            tier: 3, built: true },
];

interface Props {
  agents: Record<string, AgentState>;
  revisionCount?: number;
}

function StatusIcon({ status }: { status: string }) {
  if (status === "running") {
    return (
      <span className="w-5 h-5 rounded-full border-2 border-indigo-400 border-t-transparent animate-spin inline-block" />
    );
  }
  if (status === "complete") {
    return (
      <span className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center text-white text-[10px] font-bold">
        ✓
      </span>
    );
  }
  if (status === "error") {
    return (
      <span className="w-5 h-5 rounded-full bg-red-500 flex items-center justify-center text-white text-[10px] font-bold">
        !
      </span>
    );
  }
  return (
    <span className="w-5 h-5 rounded-full border border-slate-600 bg-slate-800" />
  );
}

const TIER_LABEL: Record<number, string> = {
  1: "Tier 1 — Data Intelligence",
  2: "Tier 2 — Financial Planning",
  3: "Tier 3 — Intelligence & Safety",
};

export default function PipelineView({ agents, revisionCount = 0 }: Props) {
  const tiers = [1, 2, 3];

  return (
    <div className="max-w-3xl mx-auto px-4 mb-10">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-base font-semibold text-white">Agent Pipeline</h2>
          {revisionCount > 0 && (
            <span className="text-xs bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-full px-3 py-1">
              Critic revision #{revisionCount}
            </span>
          )}
        </div>

        <div className="space-y-5">
          {tiers.map((tier) => (
            <div key={tier}>
              <p className="text-[11px] text-slate-500 uppercase tracking-widest mb-2">
                {TIER_LABEL[tier]}
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {ALL_AGENTS.filter((a) => a.tier === tier).map((agent) => {
                  const state = agents[agent.key];
                  const status = state?.status ?? "idle";
                  const isRunning = status === "running";
                  const isComplete = status === "complete";

                  return (
                    <div
                      key={agent.key}
                      className={`flex items-center gap-3 rounded-xl px-3 py-2.5 border transition-colors ${
                        isRunning
                          ? "border-indigo-500/40 bg-indigo-500/5"
                          : isComplete
                          ? "border-emerald-500/30 bg-emerald-500/5"
                          : "border-slate-800 bg-slate-800/50"
                      }`}
                    >
                      <StatusIcon status={status} />
                      <div className="min-w-0 flex-1">
                        <p className="text-xs text-white truncate">{agent.label}</p>
                        {isRunning && (
                          <p className="text-[10px] text-indigo-400 animate-pulse">running…</p>
                        )}
                        {isComplete && state?.summary && (
                          <AgentSummary summary={state.summary} />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function AgentSummary({ summary }: { summary: Record<string, unknown> }) {
  const entries = Object.entries(summary)
    .filter(([, v]) => v !== null && v !== undefined)
    .slice(0, 2);
  if (!entries.length) return null;
  return (
    <p className="text-[10px] text-slate-400 truncate">
      {entries.map(([k, v]) => `${k}: ${v}`).join(" · ")}
    </p>
  );
}
