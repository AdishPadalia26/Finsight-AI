"use client";

import { useState } from "react";
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { SSEEvent } from "@/lib/types";
import { getGradeColor, getScoreColor } from "@/lib/utils";
import { displayText } from "@/lib/display";

interface Props {
  data: SSEEvent;
}

type Tab = "budget" | "investment" | "stress" | "compliance";

const TABS: { id: Tab; label: string }[] = [
  { id: "budget",     label: "Budget" },
  { id: "investment", label: "Investment" },
  { id: "stress",     label: "Stress Test" },
  { id: "compliance", label: "Compliance" },
];

const PIE_COLORS = ["#6366f1", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

export default function ResultsDashboard({ data }: Props) {
  const [tab, setTab] = useState<Tab>("budget");

  const report    = (data.final_report ?? {}) as Record<string, unknown>;
  const audit     = (data.compliance_audit ?? {}) as Record<string, unknown>;
  const scores    = (data.critic_scores ?? {}) as Record<string, unknown>;
  const budget    = (report.budget_recommendation ?? {}) as Record<string, unknown>;
  const investment = (report.investment_strategy ?? {}) as Record<string, unknown>;

  return (
    <div className="max-w-3xl mx-auto px-4 mb-10">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden">
        {/* Tab bar */}
        <div className="flex border-b border-slate-800">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex-1 text-sm py-3 font-medium transition-colors ${
                tab === t.id
                  ? "text-white border-b-2 border-indigo-500"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {tab === "budget"     && <BudgetTab budget={budget} />}
          {tab === "investment" && <InvestmentTab investment={investment} />}
          {tab === "stress"     && <StressTab scores={scores} />}
          {tab === "compliance" && <ComplianceTab audit={audit} errors={data.pipeline_errors} />}
        </div>
      </div>
    </div>
  );
}

function BudgetTab({ budget }: { budget: Record<string, unknown> }) {
  const healthScore = (budget.health_score as Record<string, unknown>) ?? {};
  const total = (healthScore.total as number) ?? 0;
  const grade = (healthScore.grade as string) ?? "—";
  const framework = (budget.recommended_framework as string) ?? "—";

  const breakdown = (budget.budget_breakdown as Record<string, unknown>) ?? {};
  const pieData = Object.entries(breakdown).map(([name, value]) => ({
    name,
    value: typeof value === "number" ? Math.round(value) : 0,
  }));

  return (
    <div>
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="text-xs text-slate-500 mb-1">Health Score</p>
          <div className="flex items-baseline gap-2">
            <span className={`text-4xl font-bold ${getScoreColor(total)}`}>{total}</span>
            <span className="text-slate-500 text-sm">/ 100</span>
            <span className={`text-2xl font-bold ml-2 ${getGradeColor(grade)}`}>{grade}</span>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-slate-500 mb-1">Framework</p>
          <p className="text-sm text-white capitalize">{framework.replace(/_/g, " ")}</p>
        </div>
      </div>

      {pieData.length > 0 && (
        <>
          <p className="text-xs text-slate-500 uppercase tracking-widest mb-3">Spending Allocation</p>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}>
                {pieData.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(v) => `$${Number(v).toLocaleString()}`} contentStyle={{ background: "#1e293b", border: "1px solid #334155" }} />
            </PieChart>
          </ResponsiveContainer>
        </>
      )}

      {!pieData.length && (
        <EmptyState message="Budget breakdown not available — run the analysis to see results." />
      )}
    </div>
  );
}

function InvestmentTab({ investment }: { investment: Record<string, unknown> }) {
  const allocation = (investment.allocation as Record<string, number>) ?? {};
  const riskAlignment = (investment.risk_alignment as string) ?? "—";
  const rationale = (investment.rationale as string) ?? "";

  const pieData = Object.entries(allocation).map(([name, value]) => ({
    name,
    value: typeof value === "number" ? Math.round(value * 100) : 0,
  }));

  return (
    <div>
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="text-xs text-slate-500 mb-1">Risk Alignment</p>
          <p className="text-base text-white capitalize">{riskAlignment}</p>
        </div>
      </div>

      {pieData.length > 0 ? (
        <>
          <p className="text-xs text-slate-500 uppercase tracking-widest mb-3">Asset Allocation</p>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={({ name, value }) => `${name} ${value}%`}>
                {pieData.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(v) => `${Number(v)}%`} contentStyle={{ background: "#1e293b", border: "1px solid #334155" }} />
            </PieChart>
          </ResponsiveContainer>
        </>
      ) : (
        <EmptyState message="Investment allocation not available." />
      )}

      {rationale && (
        <div className="mt-4 bg-slate-800 rounded-xl p-4">
          <p className="text-xs text-slate-500 mb-1">Rationale</p>
          <p className="text-sm text-slate-300">{rationale}</p>
        </div>
      )}
    </div>
  );
}

const STRESS_SCENARIOS = [
  "JOB_LOSS",
  "MARKET_CRASH",
  "MEDICAL_EMERGENCY",
  "RATE_SPIKE",
  "INFLATION_SPIKE",
];

function StressTab({ scores }: { scores: Record<string, unknown> }) {
  const scenarioScores = (scores.scores as Record<string, number>) ?? {};
  const status = (scores.status as string) ?? "—";

  const radarData = STRESS_SCENARIOS.map((s) => ({
    scenario: s.replace(/_/g, " ").toLowerCase().replace(/^\w/, (c) => c.toUpperCase()),
    score: scenarioScores[s] ?? 0,
  }));

  const hasScores = Object.keys(scenarioScores).length > 0;

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <p className="text-xs text-slate-500">Critic Status:</p>
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
          status.includes("APPROVED")
            ? "bg-emerald-500/20 text-emerald-400"
            : status === "NEEDS_REVISION"
            ? "bg-amber-500/20 text-amber-400"
            : "bg-slate-700 text-slate-400"
        }`}>
          {status.replace(/_/g, " ")}
        </span>
      </div>

      {hasScores ? (
        <ResponsiveContainer width="100%" height={280}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis dataKey="scenario" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <Radar name="Resilience" dataKey="score" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
            <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155" }} />
          </RadarChart>
        </ResponsiveContainer>
      ) : (
        <EmptyState message="Stress test scores not available." />
      )}

      {hasScores && (
        <div className="grid grid-cols-5 gap-2 mt-4">
          {STRESS_SCENARIOS.map((s) => {
            const score = scenarioScores[s] ?? 0;
            return (
              <div key={s} className="text-center bg-slate-800 rounded-lg p-2">
                <p className={`text-xl font-bold ${getScoreColor(score * 10)}`}>{score}</p>
                <p className="text-[9px] text-slate-500 mt-0.5 leading-tight">
                  {s.replace(/_/g, " ")}
                </p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function ComplianceTab({
  audit,
  errors,
}: {
  audit: Record<string, unknown>;
  errors?: string[];
}) {
  const action   = (audit.action as string)   ?? "—";
  const auditId  = (audit.audit_id as string) ?? "—";
  const disclaimer = (audit.disclaimer as string) ?? "";

  const isApproved = action === "APPROVED" || action === "REWRITTEN";

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <div>
          <p className="text-xs text-slate-500 mb-1">Action</p>
          <span className={`text-sm font-semibold px-3 py-1 rounded-full ${
            isApproved
              ? "bg-emerald-500/20 text-emerald-400"
              : "bg-red-500/20 text-red-400"
          }`}>
            {action}
          </span>
        </div>
        <div>
          <p className="text-xs text-slate-500 mb-1">Audit ID</p>
          <p className="text-sm text-slate-300 font-mono">{auditId}</p>
        </div>
      </div>

      {disclaimer && (
        <div className="bg-slate-800 rounded-xl p-4 border border-slate-700">
          <p className="text-xs text-slate-500 uppercase tracking-widest mb-2">Disclaimer</p>
          <p className="text-xs text-slate-400 leading-relaxed">{disclaimer}</p>
        </div>
      )}

      {errors && errors.length > 0 && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
          <p className="text-xs text-red-400 uppercase tracking-widest mb-2">Pipeline Errors</p>
          <ul className="space-y-1">
            {errors.map((e, i) => (
              <li key={i} className="text-xs text-red-300">{displayText(e)}</li>
            ))}
          </ul>
        </div>
      )}

      {!errors?.length && !disclaimer && (
        <EmptyState message="Compliance audit not yet available." />
      )}
    </div>
  );
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="text-center py-8">
      <p className="text-sm text-slate-500">{message}</p>
    </div>
  );
}
