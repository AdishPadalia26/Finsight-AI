"use client";

import { useState } from "react";
import { displayText } from "@/lib/display";

interface PriorityAction {
  rank?: number;
  action?: string;
  domain?: string;
  rationale?: string;
  timeline?: string;
  estimated_monthly_impact?: string | number;
}

interface Props {
  advice: Record<string, unknown>;
}

function ActionCard({ action, index }: { action: PriorityAction; index: number }) {
  const domainColor: Record<string, string> = {
    budget:     "bg-amber-500/10 text-amber-400 border-amber-500/20",
    investment: "bg-indigo-500/10 text-indigo-400 border-indigo-500/20",
    debt:       "bg-red-500/10 text-red-400 border-red-500/20",
    tax:        "bg-green-500/10 text-green-400 border-green-500/20",
    goals:      "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
    savings:    "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  };
  const domain = String(action.domain ?? "").toLowerCase();
  const colorClass = domainColor[domain] ?? "bg-gray-700/30 text-gray-400 border-gray-700";
  const title = displayText(action.action) || displayText(action) || "-";
  const rationale = displayText(action.rationale);
  const timeline = displayText(action.timeline);
  const impact = displayText(action.estimated_monthly_impact);

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
      <div className="flex items-start gap-3">
        <span className="text-lg font-display text-amber-500 shrink-0 w-6 text-center">
          {action.rank ?? index + 1}
        </span>
        <div className="flex-1 space-y-1.5">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="text-sm text-white font-ui font-medium">{title}</p>
            {action.domain && (
              <span className={`text-[9px] font-jet px-1.5 py-0.5 rounded border ${colorClass}`}>
                {action.domain}
              </span>
            )}
          </div>
          {rationale && (
            <p className="text-xs text-gray-500 font-ui leading-relaxed">{rationale}</p>
          )}
          <div className="flex items-center gap-4 mt-1">
            {timeline && (
              <span className="text-[10px] text-gray-600 font-jet">{timeline}</span>
            )}
            {impact && (
              <span className="text-[10px] text-emerald-400 font-jet">
                Impact: {impact}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function AdviceDashboard({ advice }: Props) {
  const [checkedItems, setCheckedItems] = useState<Record<number, boolean>>({});

  if (!advice || Object.keys(advice).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-600 font-ui">
        Personalised advice not available
      </div>
    );
  }

  const executive = String(advice.executive_summary ?? "");
  const narrative = String(advice.financial_health_narrative ?? "");
  const actionsRaw = advice.priority_actions;
  const actions: PriorityAction[] = Array.isArray(actionsRaw) ? actionsRaw : [];
  const checklistRaw = advice.next_30_day_checklist;
  const checklist: unknown[] = Array.isArray(checklistRaw) ? checklistRaw : [];
  const insightsRaw = advice.personalised_insights;
  const insights: unknown[] = Array.isArray(insightsRaw) ? insightsRaw : [];
  const risksRaw = advice.key_risks;
  const risks: unknown[] = Array.isArray(risksRaw) ? risksRaw : [];
  const benchmark = displayText(advice.benchmark_comparison) || "";
  const roadmap = (advice.wealth_building_roadmap as Record<string, unknown>) ?? {};
  const crossInsightsRaw = advice.cross_domain_insights;
  const crossInsights: unknown[] = Array.isArray(crossInsightsRaw) ? crossInsightsRaw : [];

  function toggleCheck(i: number) {
    setCheckedItems((prev) => ({ ...prev, [i]: !prev[i] }));
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Executive summary */}
      {executive && (
        <div className="bg-amber-500/5 border border-amber-500/15 rounded-xl p-4">
          <p className="text-[9px] font-jet text-amber-500/60 tracking-widest mb-2">EXECUTIVE SUMMARY</p>
          <p className="text-sm text-gray-200 font-ui leading-relaxed">{executive}</p>
        </div>
      )}

      {/* Narrative */}
      {narrative && !narrative.startsWith("undefined") && narrative !== executive && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">FINANCIAL HEALTH NARRATIVE</p>
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
            <p className="text-xs text-gray-400 font-ui leading-relaxed">{narrative}</p>
          </div>
        </div>
      )}

      {/* Cross-domain insights */}
      {crossInsights.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">CROSS-DOMAIN INSIGHTS</p>
          <div className="space-y-2">
            {crossInsights.map((insight, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-gray-900/60 border border-indigo-500/10 rounded-lg p-3">
                <span className="text-indigo-400 shrink-0 mt-0.5">◆</span>
                <p className="text-xs text-gray-400 font-ui leading-relaxed">{displayText(insight)}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Priority actions */}
      {actions.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">PRIORITY ACTIONS</p>
          <div className="space-y-2">
            {actions.slice(0, 8).map((action, i) => (
              typeof action === "string"
                ? (
                  <div key={i} className="flex items-start gap-2.5 bg-gray-900/60 border border-gray-800 rounded-xl p-3">
                    <span className="text-amber-500 font-jet text-sm shrink-0">{i + 1}</span>
                    <p className="text-xs text-white font-ui">{displayText(action)}</p>
                  </div>
                )
                : <ActionCard key={i} action={action} index={i} />
            ))}
          </div>
        </div>
      )}

      {/* Wealth building roadmap */}
      {Object.keys(roadmap).length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">WEALTH-BUILDING ROADMAP</p>
          <div className="space-y-2">
            {(["near_term", "mid_term", "long_term"] as const).map((phase) => {
              const p = roadmap[phase] as Record<string, unknown> | undefined;
              if (!p) return null;
              const labels: Record<string, string> = {
                near_term: "0–12 months",
                mid_term: "1–3 years",
                long_term: "3+ years",
              };
              return (
                <div key={phase} className="bg-gray-900/60 border border-gray-800 rounded-xl p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[9px] font-jet text-amber-500">{labels[phase]}</span>
                    {p.focus != null && <span className="text-[10px] text-white font-jet">- {displayText(p.focus)}</span>}
                  </div>
                  {p.milestones != null && (
                    <p className="text-xs text-gray-500 font-ui">{displayText(p.milestones)}</p>
                  )}
                  {Array.isArray(p.focus_areas) && p.focus_areas.length > 0 && (
                    <ul className="mt-1 space-y-0.5">
                      {(p.focus_areas as unknown[]).map((f, i) => (
                        <li key={i} className="text-xs text-gray-500 font-ui">- {displayText(f)}</li>
                      ))}
                    </ul>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Key risks */}
      {risks.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">KEY RISKS</p>
          <div className="space-y-2">
            {risks.map((risk, i) => (
              <div key={i} className="bg-red-500/5 border border-red-500/15 rounded-xl p-3">
                <p className="text-xs text-red-300 font-ui font-medium">
                  {displayText(risk)}
                </p>
                {typeof risk === "object" && risk != null && Boolean((risk as Record<string, unknown>).mitigation) && (
                  <p className="text-xs text-gray-500 font-ui mt-1">
                    Mitigation: {displayText((risk as Record<string, unknown>).mitigation)}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Personalised insights */}
      {insights.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">PERSONALISED INSIGHTS</p>
          <div className="space-y-2">
            {insights.map((insight, i) => (
              <div key={i} className="flex items-start gap-2.5 bg-emerald-500/5 border border-emerald-500/10 rounded-lg p-3">
                <span className="text-emerald-400 shrink-0 mt-0.5">✦</span>
                <p className="text-xs text-gray-400 font-ui leading-relaxed">{displayText(insight)}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Benchmark comparison */}
      {benchmark && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">BENCHMARK COMPARISON</p>
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-3">
            <p className="text-xs text-gray-400 font-ui leading-relaxed">{benchmark}</p>
          </div>
        </div>
      )}

      {/* 30-day checklist */}
      {checklist.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">NEXT 30-DAY CHECKLIST</p>
          <div className="space-y-2">
            {checklist.slice(0, 10).map((item, i) => (
              <button
                key={i}
                onClick={() => toggleCheck(i)}
                className="w-full flex items-start gap-3 text-left bg-gray-900/60 border border-gray-800 rounded-xl p-3 hover:border-gray-700 transition-colors"
              >
                <span className={`shrink-0 w-4 h-4 rounded border mt-0.5 flex items-center justify-center text-[9px] ${
                  checkedItems[i]
                    ? "bg-emerald-500 border-emerald-500 text-white"
                    : "border-gray-600"
                }`}>
                  {checkedItems[i] ? "✓" : ""}
                </span>
                <p className={`text-xs font-ui leading-relaxed ${checkedItems[i] ? "line-through text-gray-600" : "text-gray-400"}`}>
                  {displayText(item)}
                </p>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
