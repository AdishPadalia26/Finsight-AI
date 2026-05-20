"use client";

import { useState } from "react";
import type { ComponentType } from "react";
import { BriefcaseBusiness, Percent, TrendingDown } from "lucide-react";

interface Scenario {
  key: string;
  label: string;
  detail: string;
  penalty: number;
  icon: ComponentType<{ size?: number; className?: string }>;
  modifier: Record<string, number | string>;
}

const SCENARIOS: Scenario[] = [
  {
    key: "job_loss",
    label: "Job Loss",
    detail: "Income drops to $0 for 3 months",
    penalty: 14,
    icon: BriefcaseBusiness,
    modifier: { job_loss_months: 3, income_multiplier: 0 },
  },
  {
    key: "market_crash",
    label: "Market Crash",
    detail: "-30% portfolio shock",
    penalty: 10,
    icon: TrendingDown,
    modifier: { market_drop_pct: 30 },
  },
  {
    key: "rate_spike",
    label: "Rate Spike",
    detail: "+2% interest on debts",
    penalty: 8,
    icon: Percent,
    modifier: { rate_change_bps: 200 },
  },
];

interface Props {
  baseProfile?: Record<string, unknown> | null;
  disabled?: boolean;
}

export default function ScenarioSimulator({ baseProfile, disabled }: Props) {
  const [active, setActive] = useState<Record<string, boolean>>({});
  const [results, setResults] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState<string | null>(null);

  async function toggleScenario(scenario: Scenario) {
    const nextActive = !active[scenario.key];
    setActive((prev) => ({ ...prev, [scenario.key]: nextActive }));
    if (!nextActive) return;

    setLoading(scenario.key);
    try {
      const res = await fetch("/api/scenario", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile: baseProfile ?? {},
          scenario: { ...scenario.modifier, penalty: scenario.penalty },
        }),
      });
      const data = await res.json();
      setResults((prev) => ({ ...prev, [scenario.key]: Number(data.delta ?? -scenario.penalty) }));
    } catch {
      setResults((prev) => ({ ...prev, [scenario.key]: -scenario.penalty }));
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="mt-4 bg-gray-900/60 border border-gray-800 rounded-2xl p-5">
      <div className="mb-4">
        <p className="text-sm font-semibold text-white font-ui">Scenario Simulator</p>
        <p className="text-xs text-gray-600 font-ui mt-0.5">
          Toggle quick stress scenarios and view estimated health-score impact.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {SCENARIOS.map((scenario) => {
          const Icon = scenario.icon;
          const isActive = !!active[scenario.key];
          const delta = results[scenario.key];
          return (
            <button
              key={scenario.key}
              onClick={() => toggleScenario(scenario)}
              disabled={disabled || loading === scenario.key}
              className={`text-left rounded-xl border p-4 transition-all ${
                isActive
                  ? "border-amber-500/50 bg-amber-500/10"
                  : "border-gray-800 bg-gray-950/30 hover:border-gray-700"
              } disabled:opacity-50`}
            >
              <div className="flex items-center justify-between">
                <Icon size={16} className={isActive ? "text-amber-400" : "text-gray-500"} />
                <span className={`text-[10px] font-jet ${isActive ? "text-amber-400" : "text-gray-600"}`}>
                  {loading === scenario.key ? "RUNNING" : isActive ? "ACTIVE" : "OFF"}
                </span>
              </div>
              <p className="mt-3 text-sm font-semibold text-white font-ui">{scenario.label}</p>
              <p className="mt-1 text-[10px] text-gray-500 font-ui">{scenario.detail}</p>
              {typeof delta === "number" && (
                <p className={`mt-3 text-xs font-jet ${delta < 0 ? "text-red-400" : "text-emerald-400"}`}>
                  {delta < 0 ? "▼" : "▲"} {Math.abs(delta)} pts
                </p>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
