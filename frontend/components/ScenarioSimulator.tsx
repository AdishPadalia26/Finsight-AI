"use client";

import { useState } from "react";

const SCENARIOS = [
  { key: "job_loss_severity",         label: "Job Loss Severity" },
  { key: "market_crash_severity",     label: "Market Crash Severity" },
  { key: "medical_emergency_cost",    label: "Medical Emergency Cost" },
  { key: "rate_spike_bps",            label: "Interest Rate Spike" },
  { key: "inflation_spike_pct",       label: "Inflation Spike" },
];

interface Props {
  onRerun: (overrides: Record<string, number>) => void;
  disabled?: boolean;
}

export default function ScenarioSimulator({ onRerun, disabled }: Props) {
  const [open, setOpen] = useState(false);
  const [values, setValues] = useState<Record<string, number>>(
    Object.fromEntries(SCENARIOS.map((s) => [s.key, 5]))
  );

  return (
    <div className="max-w-3xl mx-auto px-4 mb-16">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full bg-slate-900 border border-slate-800 rounded-2xl px-6 py-4 flex items-center justify-between text-left hover:border-slate-700 transition-colors"
      >
        <span className="text-sm font-medium text-white">
          Scenario Simulator
          <span className="ml-2 text-xs text-slate-500">
            — adjust stress parameters and re-run
          </span>
        </span>
        <span className="text-slate-400 text-lg">{open ? "−" : "+"}</span>
      </button>

      {open && (
        <div className="bg-slate-900 border border-t-0 border-slate-800 rounded-b-2xl px-6 pb-6">
          <p className="text-xs text-slate-500 pt-4 mb-5">
            Drag the sliders to adjust stress parameters (1 = mild, 10 = severe), then re-run the
            Critic to see how the plan holds up.
          </p>

          <div className="space-y-4 mb-6">
            {SCENARIOS.map((s) => (
              <div key={s.key}>
                <div className="flex justify-between mb-1">
                  <label className="text-xs text-slate-300">{s.label}</label>
                  <span className="text-xs font-mono text-indigo-400 w-4 text-right">
                    {values[s.key]}
                  </span>
                </div>
                <input
                  type="range"
                  min={1}
                  max={10}
                  value={values[s.key]}
                  onChange={(e) =>
                    setValues((v) => ({ ...v, [s.key]: parseInt(e.target.value) }))
                  }
                  className="w-full accent-indigo-500"
                  disabled={disabled}
                />
              </div>
            ))}
          </div>

          <button
            onClick={() => onRerun(values)}
            disabled={disabled}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-sm font-semibold py-2.5 rounded-xl transition-colors"
          >
            {disabled ? "Running..." : "Re-run with These Scenarios"}
          </button>
        </div>
      )}
    </div>
  );
}
