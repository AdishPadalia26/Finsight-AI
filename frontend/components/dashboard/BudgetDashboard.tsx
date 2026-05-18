"use client";

import { useEffect, useRef, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Cell,
  Tooltip,
} from "recharts";

interface Props {
  budget: Record<string, unknown>;
}

function RingGauge({ score }: { score: number }) {
  const [display, setDisplay] = useState(0);
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const clipped = Math.max(0, Math.min(100, score));
  const strokeDash = (display / 100) * circumference;
  const color =
    clipped >= 70 ? "#10B981" : clipped >= 40 ? "#F59E0B" : "#EF4444";

  useEffect(() => {
    let frame: number;
    let start: number | null = null;
    const duration = 1200;
    function step(ts: number) {
      if (!start) start = ts;
      const progress = Math.min((ts - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplay(Math.round(eased * clipped));
      if (progress < 1) frame = requestAnimationFrame(step);
    }
    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [clipped]);

  const grade =
    clipped >= 90 ? "A" : clipped >= 80 ? "B" : clipped >= 65 ? "C" : clipped >= 50 ? "D" : "F";
  const gradeColor =
    grade === "A" || grade === "B"
      ? "text-emerald-400"
      : grade === "C"
      ? "text-amber-400"
      : "text-red-400";

  return (
    <div className="flex flex-col items-center">
      <svg width={120} height={120} viewBox="0 0 100 100">
        <circle
          cx="50" cy="50" r={radius}
          fill="none"
          stroke="#1F2937"
          strokeWidth="8"
        />
        <circle
          cx="50" cy="50" r={radius}
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeDasharray={`${strokeDash} ${circumference}`}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
          style={{ transition: "stroke-dasharray 0.05s linear" }}
        />
        <text x="50" y="44" textAnchor="middle" fontSize="18" fontWeight="700" fill="white" fontFamily="JetBrains Mono">
          {display}
        </text>
        <text x="50" y="56" textAnchor="middle" fontSize="7" fill="#6B7280" fontFamily="Sora">
          /100
        </text>
      </svg>
      <div className="mt-1 flex items-center gap-2">
        <span className={`text-2xl font-display ${gradeColor}`}>{grade}</span>
        <span className="text-xs text-gray-500 font-ui">health score</span>
      </div>
    </div>
  );
}

function MetricCard({
  label,
  value,
  sub,
  positive,
}: {
  label: string;
  value: string;
  sub?: string;
  positive?: boolean;
}) {
  return (
    <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3">
      <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-1.5">{label}</p>
      <p
        className={`text-lg font-jet font-semibold ${
          positive === true
            ? "text-emerald-400"
            : positive === false
            ? "text-red-400"
            : "text-white"
        }`}
      >
        {value}
      </p>
      {sub && <p className="text-[10px] text-gray-600 font-ui mt-0.5">{sub}</p>}
    </div>
  );
}

export default function BudgetDashboard({ budget }: Props) {
  if (!budget || Object.keys(budget).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-600 font-ui">
        Budget data not available
      </div>
    );
  }

  const healthScore = (budget.health_score as Record<string, unknown>) ?? {};
  const total = (healthScore.total as number) ?? 0;
  const framework = (budget.recommended_framework as string) ?? "—";
  const breakdown = (budget.budget_breakdown as Record<string, number>) ?? {};
  const actionItems = (budget.action_items as string[]) ?? [];
  const monthlySurplus = (budget.monthly_surplus as number) ?? 0;
  const savingsRate = (budget.savings_rate as number) ?? 0;
  const dti = (budget.debt_to_income as number) ?? 0;
  const emergencyMonths = (budget.emergency_fund_months as number) ?? 0;

  const barData = Object.entries(breakdown)
    .filter(([, v]) => typeof v === "number" && v > 0)
    .slice(0, 8)
    .map(([name, current]) => ({
      name: name.replace(/_/g, " "),
      current: Math.round(current),
    }));

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Score + framework */}
      <div className="flex items-start gap-6">
        <RingGauge score={total} />
        <div className="flex-1 grid grid-cols-2 gap-2.5">
          <MetricCard
            label="SAVINGS RATE"
            value={`${typeof savingsRate === "number" ? (savingsRate > 1 ? savingsRate : savingsRate * 100).toFixed(1) : "—"}%`}
            positive={typeof savingsRate === "number" && (savingsRate > 1 ? savingsRate : savingsRate * 100) >= 20}
          />
          <MetricCard
            label="DEBT-TO-INCOME"
            value={`${typeof dti === "number" ? (dti > 1 ? dti : dti * 100).toFixed(1) : "—"}%`}
            positive={typeof dti === "number" && (dti > 1 ? dti : dti * 100) < 36}
          />
          <MetricCard
            label="EMERGENCY FUND"
            value={`${typeof emergencyMonths === "number" ? emergencyMonths.toFixed(1) : "—"} mo`}
            positive={typeof emergencyMonths === "number" && emergencyMonths >= 3}
          />
          <MetricCard
            label="MONTHLY SURPLUS"
            value={
              monthlySurplus !== 0
                ? `${monthlySurplus >= 0 ? "+" : ""}$${Math.abs(monthlySurplus).toLocaleString()}`
                : "—"
            }
            positive={monthlySurplus > 0}
          />
        </div>
      </div>

      {/* Framework badge */}
      <div className="flex items-center gap-2">
        <span className="text-[9px] font-jet text-gray-600 tracking-widest">BUDGET FRAMEWORK</span>
        <span className="text-[10px] font-jet text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2 py-0.5 rounded">
          {framework.replace(/_/g, " ").toUpperCase()}
        </span>
      </div>

      {/* Spending breakdown */}
      {barData.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">
            SPENDING BREAKDOWN
          </p>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={barData} layout="vertical" margin={{ left: 0 }}>
              <XAxis
                type="number"
                tick={{ fill: "#4B5563", fontSize: 9, fontFamily: "JetBrains Mono" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `$${v.toLocaleString()}`}
              />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fill: "#6B7280", fontSize: 9, fontFamily: "Sora" }}
                axisLine={false}
                tickLine={false}
                width={80}
              />
              <Tooltip
                contentStyle={{
                  background: "#111827",
                  border: "1px solid #1F2937",
                  borderRadius: "8px",
                  fontSize: "11px",
                  fontFamily: "JetBrains Mono",
                }}
                formatter={(v) => [`$${Number(v).toLocaleString()}`, "Current"]}
              />
              <Bar dataKey="current" radius={[0, 3, 3, 0]}>
                {barData.map((_, i) => (
                  <Cell key={i} fill="#F59E0B" fillOpacity={0.7} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Action items */}
      {actionItems.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">
            90-DAY ACTION ITEMS
          </p>
          <ol className="space-y-2">
            {actionItems.slice(0, 5).map((item, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <span className="text-[10px] font-jet text-amber-500 shrink-0 mt-0.5">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <p className="text-xs text-gray-400 font-ui leading-relaxed">{item}</p>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
