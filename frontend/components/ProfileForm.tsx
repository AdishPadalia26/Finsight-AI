"use client";

import { useState, useEffect } from "react";
import type { FinancialProfile } from "@/lib/types";

const DEFAULT: FinancialProfile = {
  age: 30,
  location: "Austin, TX",
  monthly_income: 6000,
  monthly_expenses: 4000,
  savings: 15000,
  investments: 5000,
  property_value: 0,
  debts: [],
  goals: [{ name: "Emergency fund", target_amount: 20000, target_years: 2, priority: "high" }],
  risk_tolerance: "moderate",
  investment_horizon: 10,
};

interface Props {
  initialValues?: Record<string, unknown> | null;
  onSubmit: (profile: FinancialProfile) => void;
  disabled?: boolean;
}

export default function ProfileForm({ initialValues, onSubmit, disabled }: Props) {
  const [form, setForm] = useState<FinancialProfile>(DEFAULT);
  const [rawMode, setRawMode] = useState(false);
  const [rawText, setRawText] = useState("");

  useEffect(() => {
    if (initialValues) {
      setForm(initialValues as unknown as FinancialProfile);
    }
  }, [initialValues]);

  function num(key: keyof FinancialProfile, value: string) {
    setForm((f) => ({ ...f, [key]: parseFloat(value) || 0 }));
  }

  function str(key: keyof FinancialProfile, value: string) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    onSubmit(form);
  }

  const field =
    "w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors";
  const label = "block text-xs text-slate-400 mb-1";

  return (
    <div className="max-w-3xl mx-auto px-4 mb-10">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-base font-semibold text-white">Financial Profile</h2>
          <button
            type="button"
            onClick={() => setRawMode((v) => !v)}
            className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors"
          >
            {rawMode ? "Switch to form" : "Free-text input"}
          </button>
        </div>

        {rawMode ? (
          <div>
            <label className={label}>Describe your financial situation</label>
            <textarea
              rows={5}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="e.g. I'm 28, living in New York, earning $7k/mo. I have $20k in savings, $5k credit card debt, and want to retire early..."
              className={`${field} resize-none`}
              disabled={disabled}
            />
            <button
              type="button"
              disabled={disabled || !rawText.trim()}
              onClick={() => onSubmit({ ...form, raw_input: rawText } as unknown as FinancialProfile)}
              className="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-sm font-semibold py-2.5 rounded-xl transition-colors"
            >
              {disabled ? "Analyzing..." : "Analyze Profile"}
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className={label}>Age</label>
                <input type="number" value={form.age} onChange={(e) => num("age", e.target.value)} className={field} min={18} max={100} disabled={disabled} />
              </div>
              <div className="col-span-2 md:col-span-2">
                <label className={label}>Location</label>
                <input type="text" value={form.location} onChange={(e) => str("location", e.target.value)} className={field} placeholder="City, State" disabled={disabled} />
              </div>
              <div>
                <label className={label}>Monthly Income ($)</label>
                <input type="number" value={form.monthly_income} onChange={(e) => num("monthly_income", e.target.value)} className={field} min={0} disabled={disabled} />
              </div>
              <div>
                <label className={label}>Monthly Expenses ($)</label>
                <input type="number" value={form.monthly_expenses} onChange={(e) => num("monthly_expenses", e.target.value)} className={field} min={0} disabled={disabled} />
              </div>
              <div>
                <label className={label}>Savings ($)</label>
                <input type="number" value={form.savings} onChange={(e) => num("savings", e.target.value)} className={field} min={0} disabled={disabled} />
              </div>
              <div>
                <label className={label}>Investments ($)</label>
                <input type="number" value={form.investments} onChange={(e) => num("investments", e.target.value)} className={field} min={0} disabled={disabled} />
              </div>
              <div>
                <label className={label}>Property Value ($)</label>
                <input type="number" value={form.property_value} onChange={(e) => num("property_value", e.target.value)} className={field} min={0} disabled={disabled} />
              </div>
              <div>
                <label className={label}>Risk Tolerance</label>
                <select value={form.risk_tolerance} onChange={(e) => str("risk_tolerance", e.target.value)} className={field} disabled={disabled}>
                  <option value="conservative">Conservative</option>
                  <option value="moderate">Moderate</option>
                  <option value="aggressive">Aggressive</option>
                </select>
              </div>
              <div>
                <label className={label}>Investment Horizon (yrs)</label>
                <input type="number" value={form.investment_horizon} onChange={(e) => num("investment_horizon", e.target.value)} className={field} min={1} max={50} disabled={disabled} />
              </div>
            </div>

            <button
              type="submit"
              disabled={disabled}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white text-sm font-semibold py-2.5 rounded-xl transition-colors"
            >
              {disabled ? "Analyzing..." : "Analyze Profile"}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
