"use client";

import { useEffect, useState } from "react";
import { displayText } from "@/lib/display";

interface Props {
  overview: Record<string, unknown>;
  advice?: Record<string, unknown>;
}

function Ring({ value, max, color }: { value: number; max: number; color: string }) {
  const [display, setDisplay] = useState(0);
  const r = 40;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(1, value / max);

  useEffect(() => {
    let raf: number;
    let start: number | null = null;
    function step(ts: number) {
      if (!start) start = ts;
      const p = Math.min((ts - start) / 1000, 1);
      setDisplay(Math.round((1 - Math.pow(1 - p, 3)) * value));
      if (p < 1) raf = requestAnimationFrame(step);
    }
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [value]);

  return (
    <div className="flex flex-col items-center">
      <svg width={96} height={96} viewBox="0 0 96 96">
        <circle cx="48" cy="48" r={r} fill="none" stroke="#1F2937" strokeWidth="7" />
        <circle
          cx="48" cy="48" r={r}
          fill="none"
          stroke={color}
          strokeWidth="7"
          strokeDasharray={`${pct * circ} ${circ}`}
          strokeLinecap="round"
          transform="rotate(-90 48 48)"
        />
        <text x="48" y="53" textAnchor="middle" fontSize="18" fontWeight="bold" fill="white" fontFamily="JetBrains Mono">
          {display}
        </text>
      </svg>
    </div>
  );
}

function KPI({
  label, value, sub, color = "text-white",
}: {
  label: string; value: string; sub?: string; color?: string;
}) {
  return (
    <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3.5">
      <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-1.5">{label}</p>
      <p className={`text-lg font-jet font-semibold ${color}`}>{value}</p>
      {sub && <p className="text-[10px] text-gray-600 font-ui mt-0.5">{sub}</p>}
    </div>
  );
}

export default function OverviewDashboard({ overview, advice }: Props) {
  if (!overview || Object.keys(overview).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-600 font-ui">
        Overview data not available
      </div>
    );
  }

  const score = Number(overview.health_score ?? 0);
  const grade = String(overview.health_grade ?? "—");
  const sr = Number(overview.savings_rate ?? 0);
  const dti = Number(overview.debt_to_income ?? 0);
  const em = Number(overview.emergency_fund_months ?? 0);
  const nw = Number(overview.net_worth ?? 0);
  const surplus = Number(overview.monthly_surplus ?? 0);
  const income = Number(overview.monthly_income ?? 0);
  const expenses = Number(overview.monthly_expenses ?? 0);

  const gradeColor =
    grade === "A" ? "#10B981" :
    grade === "B" ? "#F59E0B" :
    grade === "C" ? "#FBBF24" :
    "#EF4444";

  const executive = displayText(advice?.executive_summary) || displayText(advice?.financial_health_narrative) || null;
  const topActions: string[] = [];
  const acts = advice?.priority_actions;
  if (Array.isArray(acts)) {
    for (const a of acts.slice(0, 3)) {
      const text =
        typeof a === "object" && a !== null
          ? displayText((a as Record<string, unknown>).action) || displayText(a)
          : displayText(a);
      if (text) topActions.push(text);
    }
  }

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Hero card */}
      <div className="flex items-center gap-6 bg-gray-900/60 border border-amber-500/15 rounded-2xl p-5">
        <div className="flex flex-col items-center">
          <Ring value={Math.round(score)} max={100} color={gradeColor} />
          <span className="text-2xl font-display mt-1" style={{ color: gradeColor }}>{grade}</span>
          <span className="text-[9px] text-gray-600 font-jet">HEALTH SCORE</span>
        </div>
        <div className="flex-1 grid grid-cols-2 gap-2.5">
          <KPI
            label="SAVINGS RATE"
            value={`${sr.toFixed(1)}%`}
            sub="target ≥ 20%"
            color={sr >= 20 ? "text-emerald-400" : sr >= 10 ? "text-amber-400" : "text-red-400"}
          />
          <KPI
            label="DEBT-TO-INCOME"
            value={`${dti.toFixed(1)}%`}
            sub="target ≤ 36%"
            color={dti <= 36 ? "text-emerald-400" : dti <= 50 ? "text-amber-400" : "text-red-400"}
          />
          <KPI
            label="EMERGENCY FUND"
            value={`${em.toFixed(1)} mo`}
            sub="target ≥ 6 months"
            color={em >= 6 ? "text-emerald-400" : em >= 3 ? "text-amber-400" : "text-red-400"}
          />
          <KPI
            label="NET WORTH"
            value={`$${Math.abs(nw).toLocaleString()}`}
            sub={nw < 0 ? "negative" : undefined}
            color={nw >= 0 ? "text-white" : "text-red-400"}
          />
        </div>
      </div>

      {/* Income / expense strip */}
      <div className="grid grid-cols-3 gap-2.5">
        <KPI label="MONTHLY INCOME" value={`$${income.toLocaleString()}`} />
        <KPI label="MONTHLY EXPENSES" value={`$${expenses.toLocaleString()}`} />
        <KPI
          label="MONTHLY SURPLUS"
          value={`${surplus >= 0 ? "+" : ""}$${Math.abs(surplus).toLocaleString()}`}
          color={surplus >= 0 ? "text-emerald-400" : "text-red-400"}
        />
      </div>

      {/* Financial health narrative */}
      {executive && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">FINANCIAL HEALTH NARRATIVE</p>
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4">
            <p className="text-xs text-gray-300 leading-relaxed font-ui">{executive}</p>
          </div>
        </div>
      )}

      {/* Top priority actions preview */}
      {topActions.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">TOP PRIORITY ACTIONS</p>
          <ol className="space-y-2">
            {topActions.map((action, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <span className="text-[10px] font-jet text-amber-500 shrink-0 mt-0.5">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <p className="text-xs text-gray-400 font-ui leading-relaxed">{action}</p>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
