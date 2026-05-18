"use client";

import { useState } from "react";
import { RotateCcw } from "lucide-react";

interface Scenario {
  key: string;
  label: string;
  min: number;
  max: number;
  unit: string;
  default: number;
  formatValue: (v: number) => string;
}

const SCENARIOS: Scenario[] = [
  {
    key: "job_loss_months",
    label: "Job Loss Duration",
    min: 1,
    max: 12,
    unit: "months",
    default: 6,
    formatValue: (v) => `${v} mo`,
  },
  {
    key: "market_drop_pct",
    label: "Market Drop",
    min: 10,
    max: 50,
    unit: "%",
    default: 30,
    formatValue: (v) => `-${v}%`,
  },
  {
    key: "medical_cost",
    label: "Emergency Expense",
    min: 10000,
    max: 100000,
    unit: "$",
    default: 50000,
    formatValue: (v) => `$${(v / 1000).toFixed(0)}k`,
  },
  {
    key: "rate_change_bps",
    label: "Rate Change",
    min: -100,
    max: 500,
    unit: "bps",
    default: 300,
    formatValue: (v) => `${v >= 0 ? "+" : ""}${(v / 100).toFixed(1)}%`,
  },
  {
    key: "inflation_spike_pct",
    label: "Inflation Spike",
    min: 3,
    max: 10,
    unit: "%",
    default: 5,
    formatValue: (v) => `+${v}%`,
  },
];

interface Props {
  onRerun: (overrides: Record<string, number>) => void;
  disabled?: boolean;
}

export default function ScenarioSimulator({ onRerun, disabled }: Props) {
  const [isOpen, setIsOpen] = useState(false);
  const [values, setValues] = useState<Record<string, number>>(
    Object.fromEntries(SCENARIOS.map((s) => [s.key, s.default]))
  );

  function handleChange(key: string, val: number) {
    setValues((v) => ({ ...v, [key]: val }));
  }

  function handleReset() {
    setValues(Object.fromEntries(SCENARIOS.map((s) => [s.key, s.default])));
  }

  return (
    <div className="mt-4">
      <button
        onClick={() => setIsOpen((v) => !v)}
        className="w-full flex items-center justify-between bg-gray-900/60 border border-gray-800 hover:border-amber-500/30 rounded-2xl px-5 py-4 transition-colors group"
      >
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-white font-ui">
            Scenario Simulator
          </span>
          <span className="text-[10px] text-gray-600 font-ui">
            — adjust stress parameters and re-run
          </span>
        </div>
        <span className="text-gray-600 group-hover:text-amber-500 transition-colors text-lg">
          {isOpen ? "−" : "+"}
        </span>
      </button>

      {isOpen && (
        <div className="bg-gray-900/40 border border-t-0 border-gray-800 rounded-b-2xl p-5">
          <p className="text-xs text-gray-500 font-ui mb-5 leading-relaxed">
            Drag sliders to adjust stress parameters, then re-run the Critic Agent to
            see how the financial plan holds up under different conditions.
          </p>

          <div className="space-y-5 mb-6">
            {SCENARIOS.map((scenario) => (
              <div key={scenario.key}>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs text-gray-300 font-ui">
                    {scenario.label}
                  </label>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-jet text-amber-400 min-w-[48px] text-right">
                      {scenario.formatValue(values[scenario.key])}
                    </span>
                  </div>
                </div>
                <input
                  type="range"
                  min={scenario.min}
                  max={scenario.max}
                  step={scenario.key === "medical_cost" ? 5000 : scenario.key === "rate_change_bps" ? 50 : 1}
                  value={values[scenario.key]}
                  onChange={(e) =>
                    handleChange(scenario.key, parseInt(e.target.value))
                  }
                  disabled={disabled}
                  className="w-full disabled:opacity-40"
                />
                <div className="flex justify-between text-[9px] font-jet text-gray-700 mt-0.5">
                  <span>{scenario.formatValue(scenario.min)}</span>
                  <span>{scenario.formatValue(scenario.max)}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleReset}
              disabled={disabled}
              className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 border border-gray-800 hover:border-gray-700 rounded-xl px-4 py-2.5 transition-colors disabled:opacity-40 font-ui"
            >
              <RotateCcw size={12} />
              Reset
            </button>
            <button
              onClick={() => onRerun(values)}
              disabled={disabled}
              className="flex-1 bg-amber-500 hover:bg-amber-400 active:bg-amber-600 disabled:bg-gray-800 disabled:cursor-not-allowed text-gray-950 disabled:text-gray-600 font-semibold py-2.5 rounded-xl transition-colors text-sm font-ui flex items-center justify-center gap-2"
            >
              {disabled ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-gray-600 border-t-transparent rounded-full animate-spin" />
                  Running…
                </>
              ) : (
                "Re-run with These Scenarios →"
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
