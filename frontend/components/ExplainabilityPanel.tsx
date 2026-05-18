"use client";

import { useState } from "react";
import type { AgentState } from "@/lib/types";

interface Props {
  agents: Record<string, AgentState>;
}

export default function ExplainabilityPanel({ agents }: Props) {
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const completedAgents = Object.entries(agents).filter(
    ([, state]) => state.status === "complete"
  );

  return (
    <div className="max-w-3xl mx-auto px-4 mb-10">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full bg-slate-900 border border-slate-800 rounded-2xl px-6 py-4 flex items-center justify-between text-left hover:border-slate-700 transition-colors"
      >
        <span className="text-sm font-medium text-white">
          Agent Reasoning Trace
          {completedAgents.length > 0 && (
            <span className="ml-2 text-xs text-slate-500">
              ({completedAgents.length} agents)
            </span>
          )}
        </span>
        <span className="text-slate-400 text-lg">{open ? "−" : "+"}</span>
      </button>

      {open && (
        <div className="bg-slate-900 border border-t-0 border-slate-800 rounded-b-2xl px-6 pb-6">
          {completedAgents.length === 0 ? (
            <p className="text-sm text-slate-500 pt-4">
              No completed agents yet.
            </p>
          ) : (
            <div className="space-y-2 pt-4">
              {completedAgents.map(([key, state]) => (
                <div key={key} className="border border-slate-800 rounded-xl overflow-hidden">
                  <button
                    onClick={() =>
                      setExpanded((e) => (e === key ? null : key))
                    }
                    className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-slate-800 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      <span className="text-sm text-white">{state.label}</span>
                    </div>
                    <span className="text-slate-500 text-sm">
                      {expanded === key ? "▲" : "▼"}
                    </span>
                  </button>

                  {expanded === key && state.summary && (
                    <div className="px-4 pb-4 bg-slate-800/50">
                      <pre className="text-xs text-slate-300 overflow-x-auto whitespace-pre-wrap">
                        {JSON.stringify(state.summary, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {process.env.NEXT_PUBLIC_LANGSMITH_URL && (
            <a
              href={process.env.NEXT_PUBLIC_LANGSMITH_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              View Full LangSmith Trace
              <span>↗</span>
            </a>
          )}
        </div>
      )}
    </div>
  );
}
