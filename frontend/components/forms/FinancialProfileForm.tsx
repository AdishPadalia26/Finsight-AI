"use client";

import { useState, useEffect } from "react";
import { DollarSign, MapPin, TrendingUp, Shield } from "lucide-react";
import type { FinancialProfile } from "@/lib/types";

const DEFAULTS: FinancialProfile = {
  age: 30,
  location: "Austin, TX",
  monthly_income: 6000,
  monthly_expenses: 4000,
  savings: 15000,
  investments: 5000,
  property_value: 0,
  debts: [],
  goals: [],
  risk_tolerance: "moderate",
  investment_horizon: 20,
};

interface Props {
  initialValues?: Record<string, unknown> | null;
  onSubmit: (profile: FinancialProfile) => void;
  disabled?: boolean;
}

const RISK_OPTIONS = [
  {
    value: "conservative" as const,
    label: "Conservative",
    desc: "Capital preservation",
    color: "border-blue-500/40 hover:border-blue-400",
    activeColor: "border-blue-400 bg-blue-500/10",
    dot: "bg-blue-400",
  },
  {
    value: "moderate" as const,
    label: "Moderate",
    desc: "Balanced growth",
    color: "border-amber-500/40 hover:border-amber-400",
    activeColor: "border-amber-400 bg-amber-500/10",
    dot: "bg-amber-400",
  },
  {
    value: "aggressive" as const,
    label: "Aggressive",
    desc: "Maximum growth",
    color: "border-cyan-500/40 hover:border-cyan-400",
    activeColor: "border-cyan-400 bg-cyan-500/10",
    dot: "bg-cyan-400",
  },
];

const field =
  "w-full bg-gray-900 border border-gray-800 focus:border-amber-500/60 rounded-lg px-3 py-2.5 text-sm text-white placeholder-gray-600 outline-none transition-colors font-ui";
const label = "block text-[10px] font-jet text-gray-600 tracking-widest mb-1.5";
const section = "space-y-4";
const sectionHeader =
  "flex items-center gap-2 text-[10px] font-jet text-gray-500 tracking-[0.2em] mb-4 mt-2";

function formatMoney(v: number) {
  return v > 0 ? `$${v.toLocaleString()}` : "";
}

export default function FinancialProfileForm({
  initialValues,
  onSubmit,
  disabled,
}: Props) {
  const [form, setForm] = useState<FinancialProfile>(DEFAULTS);

  useEffect(() => {
    if (initialValues) {
      setForm((prev) => ({ ...prev, ...(initialValues as Partial<FinancialProfile>) }));
    }
  }, [initialValues]);

  function setNum(key: keyof FinancialProfile, val: string) {
    setForm((f) => ({ ...f, [key]: parseFloat(val.replace(/,/g, "")) || 0 }));
  }

  function setStr(key: keyof FinancialProfile, val: string) {
    setForm((f) => ({ ...f, [key]: val }));
  }

  const savings_rate =
    form.monthly_income > 0
      ? (((form.monthly_income - form.monthly_expenses) / form.monthly_income) * 100).toFixed(1)
      : "—";

  const net_worth =
    form.savings +
    form.investments +
    form.property_value -
    (form.debts?.reduce((s, d) => s + (d.balance || 0), 0) ?? 0);

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
        <h2 className="text-sm font-semibold text-white font-ui">Financial Profile</h2>
        <div className="flex items-center gap-3 text-[10px] font-jet">
          <span className="text-gray-600">
            Savings rate:{" "}
            <span
              className={
                parseFloat(savings_rate) >= 20
                  ? "text-emerald-400"
                  : parseFloat(savings_rate) >= 10
                  ? "text-amber-400"
                  : "text-red-400"
              }
            >
              {savings_rate}%
            </span>
          </span>
          <span className="text-gray-600">
            Net worth:{" "}
            <span className={net_worth >= 0 ? "text-emerald-400" : "text-red-400"}>
              {net_worth >= 0 ? "+" : ""}
              {formatMoney(Math.abs(net_worth))}
            </span>
          </span>
        </div>
      </div>

      <div className="p-5 space-y-6">
        {/* Personal */}
        <div className={section}>
          <div className={sectionHeader}>
            <MapPin size={10} />
            PERSONAL
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className={label}>AGE</label>
              <input
                type="number"
                value={form.age}
                onChange={(e) => setNum("age", e.target.value)}
                className={field}
                min={18}
                max={100}
                disabled={disabled}
              />
            </div>
            <div className="col-span-2">
              <label className={label}>LOCATION</label>
              <input
                type="text"
                value={form.location}
                onChange={(e) => setStr("location", e.target.value)}
                className={field}
                placeholder="City, State"
                disabled={disabled}
              />
            </div>
          </div>
        </div>

        {/* Income & Expenses */}
        <div className={section}>
          <div className={sectionHeader}>
            <DollarSign size={10} />
            INCOME &amp; EXPENSES
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={label}>MONTHLY INCOME</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 text-sm">$</span>
                <input
                  type="number"
                  value={form.monthly_income}
                  onChange={(e) => setNum("monthly_income", e.target.value)}
                  className={`${field} pl-6`}
                  min={0}
                  disabled={disabled}
                />
              </div>
            </div>
            <div>
              <label className={label}>MONTHLY EXPENSES</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 text-sm">$</span>
                <input
                  type="number"
                  value={form.monthly_expenses}
                  onChange={(e) => setNum("monthly_expenses", e.target.value)}
                  className={`${field} pl-6`}
                  min={0}
                  disabled={disabled}
                />
              </div>
            </div>
          </div>
          {/* Surplus bar */}
          {form.monthly_income > 0 && (
            <div className="flex items-center gap-2 mt-2">
              <div className="flex-1 h-1 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${
                    form.monthly_expenses / form.monthly_income > 0.9
                      ? "bg-red-500"
                      : form.monthly_expenses / form.monthly_income > 0.7
                      ? "bg-amber-500"
                      : "bg-emerald-500"
                  }`}
                  style={{
                    width: `${Math.min((form.monthly_expenses / form.monthly_income) * 100, 100)}%`,
                  }}
                />
              </div>
              <span className="text-[10px] font-jet text-gray-600">
                {((form.monthly_expenses / form.monthly_income) * 100).toFixed(0)}% of income
              </span>
            </div>
          )}
        </div>

        {/* Assets */}
        <div className={section}>
          <div className={sectionHeader}>
            <TrendingUp size={10} />
            ASSETS
          </div>
          <div className="grid grid-cols-3 gap-3">
            {[
              { key: "savings" as const, label: "SAVINGS" },
              { key: "investments" as const, label: "INVESTMENTS" },
              { key: "property_value" as const, label: "PROPERTY VALUE" },
            ].map(({ key, label: lbl }) => (
              <div key={key}>
                <label className={label}>{lbl}</label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 text-sm">$</span>
                  <input
                    type="number"
                    value={form[key] as number}
                    onChange={(e) => setNum(key, e.target.value)}
                    className={`${field} pl-6`}
                    min={0}
                    disabled={disabled}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Debts summary (read-only display) */}
        {form.debts && form.debts.length > 0 && (
          <div>
            <div className={sectionHeader}>
              <Shield size={10} />
              DEBTS ({form.debts.length})
            </div>
            <div className="space-y-1.5">
              {form.debts.map((d, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between bg-gray-800/50 rounded-lg px-3 py-2"
                >
                  <span className="text-xs text-gray-400 font-ui capitalize">
                    {String(d.type).replace(/_/g, " ")}
                  </span>
                  <div className="flex items-center gap-3 font-jet text-xs">
                    <span className="text-red-400">
                      ${Number(d.balance).toLocaleString()}
                    </span>
                    <span className="text-gray-600">
                      {Number(d.interest_rate).toFixed(1)}% APR
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Goals summary (read-only display) */}
        {form.goals && form.goals.length > 0 && (
          <div>
            <div className={sectionHeader}>
              <TrendingUp size={10} />
              GOALS ({form.goals.length})
            </div>
            <div className="space-y-1.5">
              {form.goals.map((g, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between bg-gray-800/50 rounded-lg px-3 py-2"
                >
                  <span className="text-xs text-gray-300 font-ui">
                    {(g as { name?: string; description?: string }).name ??
                     (g as { name?: string; description?: string }).description ?? "Goal"}
                  </span>
                  <span className="font-jet text-xs text-amber-400">
                    $
                    {Number(g.target_amount).toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Risk tolerance */}
        <div>
          <div className={sectionHeader}>
            <Shield size={10} />
            RISK PROFILE
          </div>
          <div className="grid grid-cols-3 gap-2 mb-4">
            {RISK_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setStr("risk_tolerance", opt.value)}
                disabled={disabled}
                className={`rounded-xl p-3 border text-left transition-all ${
                  form.risk_tolerance === opt.value
                    ? opt.activeColor
                    : opt.color
                } disabled:opacity-40`}
              >
                <div className={`w-2 h-2 rounded-full ${opt.dot} mb-2`} />
                <p className="text-xs font-semibold text-white font-ui">{opt.label}</p>
                <p className="text-[10px] text-gray-600 font-ui mt-0.5">{opt.desc}</p>
              </button>
            ))}
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className={label}>INVESTMENT HORIZON</label>
              <span className="text-xs font-jet text-amber-400">
                {form.investment_horizon} yrs
              </span>
            </div>
            <input
              type="range"
              min={1}
              max={50}
              value={form.investment_horizon}
              onChange={(e) => setNum("investment_horizon", e.target.value)}
              className="w-full"
              disabled={disabled}
            />
          </div>
        </div>

        {/* Submit */}
        <button
          type="button"
          onClick={() => onSubmit(form)}
          disabled={disabled}
          className="w-full bg-amber-500 hover:bg-amber-400 active:bg-amber-600 disabled:bg-gray-800 disabled:cursor-not-allowed text-gray-950 disabled:text-gray-600 font-semibold py-3 rounded-xl transition-colors text-sm font-ui tracking-wide flex items-center justify-center gap-2"
        >
          {disabled ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-gray-600 border-t-transparent rounded-full animate-spin" />
              Analyzing…
            </>
          ) : (
            "Run Analysis →"
          )}
        </button>
      </div>
    </div>
  );
}
