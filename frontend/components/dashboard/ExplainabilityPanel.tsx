"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, ExternalLink } from "lucide-react";
import type { AgentState } from "@/lib/types";

interface Props {
  agents: Record<string, AgentState>;
}

const AGENT_TIER: Record<string, string> = {
  profile_builder: "Tier 1",
  behavioral_pattern: "Tier 1",
  credit_intelligence: "Tier 1",
  budget_architect: "Tier 2",
  goal_engineering: "Tier 2",
  investment_strategist: "Tier 2",
  tax_intelligence: "Tier 2",
  debt_elimination: "Tier 2",
  life_event: "Tier 3",
  critic: "Tier 3",
  compliance: "Tier 3",
  memory: "Tier 3",
};

const TIER_COLOR: Record<string, string> = {
  "Tier 1": "text-blue-400",
  "Tier 2": "text-amber-400",
  "Tier 3": "text-cyan-400",
};

function SummaryEntry({ k, v }: { k: string; v: unknown }) {
  const display =
    typeof v === "object" && v !== null
      ? JSON.stringify(v).slice(0, 120) + (JSON.stringify(v).length > 120 ? "…" : "")
      : String(v);

  return (
    <div className="flex items-start gap-3 text-xs">
      <span className="font-jet text-gray-600 shrink-0 min-w-[120px]">
        {k.replace(/_/g, " ")}
      </span>
      <span className="text-gray-400 font-ui break-words">{display}</span>
    </div>
  );
}

export default function ExplainabilityPanel({ agents }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const completed = Object.entries(agents).filter(
    ([, s]) => s.status === "complete"
  );

  if (completed.length === 0) return null;

  return (
    <div className="mt-4">
      <button
        onClick={() => setIsOpen((v) => !v)}
        className="w-full flex items-center justify-between bg-gray-900/60 border border-gray-800 hover:border-gray-700 rounded-2xl px-5 py-4 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-white font-ui">
            {isOpen ? "▾ Agent Trace" : "▸ Agent Trace"}
          </span>
          <span className="text-[10px] font-jet text-gray-600">
            {completed.length} agents
          </span>
        </div>
        {isOpen ? (
          <ChevronUp size={16} className="text-gray-500" />
        ) : (
          <ChevronDown size={16} className="text-gray-500" />
        )}
      </button>

      {isOpen && (
        <div className="animate-slide-down bg-gray-900/40 border border-t-0 border-gray-800 rounded-b-2xl p-4 space-y-2">
          {completed.map(([key, state]) => {
            const tier = AGENT_TIER[key] ?? "—";
            const tierColor = TIER_COLOR[tier] ?? "text-gray-400";
            const isExpanded = expanded === key;
            const summaryEntries = state.summary
              ? Object.entries(state.summary).filter(([, v]) => v != null)
              : [];

            return (
              <div key={key} className="border border-gray-800 rounded-xl overflow-hidden">
                <button
                  onClick={() => setExpanded(isExpanded ? null : key)}
                  className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-800/40 transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="w-2 h-2 rounded-full bg-cyan-400" />
                    <span className="text-xs font-semibold text-amber-300 font-ui">
                      {state.label}
                    </span>
                    <span className={`text-[9px] font-jet ${tierColor}`}>{tier}</span>
                  </div>
                  {isExpanded ? (
                    <ChevronUp size={12} className="text-gray-600" />
                  ) : (
                    <ChevronDown size={12} className="text-gray-600" />
                  )}
                </button>

                {isExpanded && (
                  <div className="px-4 pb-4 bg-gray-800/20 border-t border-gray-800">
                    {summaryEntries.length > 0 ? (
                      <div className="space-y-2 pt-3">
                        {summaryEntries.map(([k, v]) => (
                          <SummaryEntry key={k} k={k} v={v} />
                        ))}
                        {summaryEntries.find(([k]) => k === "audit_id") && (
                          <p className="text-[10px] font-jet text-gray-600">
                            audit: {String(summaryEntries.find(([k]) => k === "audit_id")?.[1])}
                          </p>
                        )}
                      </div>
                    ) : (
                      <p className="text-xs text-gray-600 font-ui pt-3">
                        No summary data available.
                      </p>
                    )}
                  </div>
                )}
              </div>
            );
          })}

          {process.env.NEXT_PUBLIC_LANGSMITH_URL && (
            <a
              href={process.env.NEXT_PUBLIC_LANGSMITH_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs text-amber-400 hover:text-amber-300 transition-colors mt-2 font-ui"
            >
              View Full LangSmith Trace
              <ExternalLink size={11} />
            </a>
          )}
        </div>
      )}
    </div>
  );
}
