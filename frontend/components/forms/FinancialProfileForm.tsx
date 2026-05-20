"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2, DollarSign, MapPin, TrendingUp, Shield, Target, ChevronDown, ChevronUp, Briefcase } from "lucide-react";
import type { FinancialProfile, Debt, Goal } from "@/lib/types";

const DEFAULTS: FinancialProfile = {
  age: 30,
  location: "Austin, TX",
  employment_status: "full_time",
  monthly_income: 6000,
  monthly_expenses: 4000,
  savings: 15000,
  investments: 5000,
  property_value: 0,
  debts: [],
  goals: [],
  risk_tolerance: "moderate",
  investment_horizon: 20,
  tax_bracket: undefined,
  recent_life_events: [],
};

const BLANK_DEBT: Debt = { type: "credit_card", balance: 0, interest_rate: 0, minimum_payment: 0 };
const BLANK_GOAL: Goal = { description: "", target_amount: 0, timeline_months: 12, priority: "high" };

const DEBT_TYPES = [
  { value: "credit_card",   label: "Credit Card" },
  { value: "student_loan",  label: "Student Loan" },
  { value: "mortgage",      label: "Mortgage" },
  { value: "auto_loan",     label: "Auto Loan" },
  { value: "personal_loan", label: "Personal Loan" },
  { value: "heloc",         label: "HELOC" },
  { value: "bnpl",          label: "Buy Now Pay Later" },
];

const GOAL_PRIORITIES = [
  { value: "critical", label: "Critical", color: "text-red-400" },
  { value: "high",     label: "High",     color: "text-amber-400" },
  { value: "medium",   label: "Medium",   color: "text-cyan-400" },
  { value: "low",      label: "Low",      color: "text-gray-400" },
];

const EMPLOYMENT_OPTIONS = [
  { value: "full_time",     label: "Full-time employed" },
  { value: "part_time",     label: "Part-time employed" },
  { value: "self_employed", label: "Self-employed / Freelance" },
  { value: "student",       label: "Student" },
  { value: "retired",       label: "Retired" },
  { value: "unemployed",    label: "Unemployed / Job seeking" },
];

const TAX_BRACKETS = [
  { value: 0.10, label: "10% — up to $11,600" },
  { value: 0.12, label: "12% — $11,601–$47,150" },
  { value: 0.22, label: "22% — $47,151–$100,525" },
  { value: 0.24, label: "24% — $100,526–$191,950" },
  { value: 0.32, label: "32% — $191,951–$243,725" },
  { value: 0.35, label: "35% — $243,726–$609,350" },
  { value: 0.37, label: "37% — over $609,350" },
];

const LIFE_EVENTS = [
  { value: "new_job",       label: "New Job" },
  { value: "promotion",     label: "Promotion / Raise" },
  { value: "job_loss",      label: "Job Loss" },
  { value: "marriage",      label: "Marriage" },
  { value: "divorce",       label: "Divorce / Separation" },
  { value: "had_child",     label: "New Child / Adoption" },
  { value: "home_purchase", label: "Home Purchase" },
  { value: "retirement",    label: "Approaching Retirement" },
  { value: "medical_expense", label: "Major Medical Expense" },
  { value: "inheritance",   label: "Inheritance / Windfall" },
  { value: "college_tuition", label: "College Tuition Starting" },
  { value: "relocation",    label: "Relocation" },
];

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
const miniField =
  "w-full bg-gray-950 border border-gray-700 focus:border-amber-500/50 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-700 outline-none transition-colors font-ui";
const label = "block text-[10px] font-jet text-gray-600 tracking-widest mb-1.5";
const section = "space-y-4";
const sectionHeader =
  "flex items-center gap-2 text-[10px] font-jet text-gray-500 tracking-[0.2em] mb-4 mt-2";

interface Props {
  initialValues?: Record<string, unknown> | null;
  onSubmit: (profile: FinancialProfile) => void;
  disabled?: boolean;
}

function formatMoney(v: number) {
  return v > 0 ? `$${v.toLocaleString()}` : "";
}

function DollarInput({
  label: lbl, value, onChange, disabled, placeholder,
}: { label: string; value: number; onChange: (v: number) => void; disabled?: boolean; placeholder?: string }) {
  return (
    <div>
      <label className={label}>{lbl}</label>
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 text-sm pointer-events-none">$</span>
        <input
          type="number"
          value={value || ""}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          className={`${field} pl-6`}
          min={0}
          disabled={disabled}
          placeholder={placeholder ?? "0"}
        />
      </div>
    </div>
  );
}

function MiniDollarInput({
  label: lbl, value, onChange, placeholder,
}: { label: string; value: number; onChange: (v: number) => void; placeholder?: string }) {
  return (
    <div>
      <label className="block text-[10px] font-jet text-gray-500 mb-1">{lbl}</label>
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 text-xs pointer-events-none">$</span>
        <input
          type="number"
          value={value || ""}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          className={`${miniField} pl-6`}
          min={0}
          placeholder={placeholder ?? "0"}
        />
      </div>
    </div>
  );
}

export default function FinancialProfileForm({ initialValues, onSubmit, disabled }: Props) {
  const [form, setForm] = useState<FinancialProfile>(DEFAULTS);
  const [errors, setErrors] = useState<{ age?: string; monthly_income?: string }>({});

  // Debt add form state
  const [addingDebt, setAddingDebt] = useState(false);
  const [newDebt, setNewDebt] = useState<Debt>(BLANK_DEBT);
  const [debtErrors, setDebtErrors] = useState<{ balance?: string }>({});

  // Goal add form state
  const [addingGoal, setAddingGoal] = useState(false);
  const [newGoal, setNewGoal] = useState<Goal>(BLANK_GOAL);
  const [goalErrors, setGoalErrors] = useState<{ description?: string; target_amount?: string }>({});

  useEffect(() => {
    if (initialValues) {
      setForm((prev) => ({
        ...prev,
        ...(initialValues as Partial<FinancialProfile>),
        // Normalize recent_life_events to always be an array
        recent_life_events: Array.isArray(initialValues.recent_life_events)
          ? (initialValues.recent_life_events as string[])
          : [],
      }));
    }
  }, [initialValues]);

  function setNum(key: keyof FinancialProfile, val: string) {
    setForm((f) => ({ ...f, [key]: parseFloat(val) || 0 }));
    if (key === "age" || key === "monthly_income") {
      setErrors((prev) => ({ ...prev, [key]: undefined }));
    }
  }

  function setStr(key: keyof FinancialProfile, val: string) {
    setForm((f) => ({ ...f, [key]: val }));
  }

  // ── Debt management ──────────────────────────────────────────────────────

  function addDebt() {
    if (newDebt.balance <= 0) {
      setDebtErrors({ balance: "Balance must be greater than 0" });
      return;
    }
    setForm((f) => ({ ...f, debts: [...(f.debts ?? []), { ...newDebt }] }));
    setNewDebt(BLANK_DEBT);
    setDebtErrors({});
    setAddingDebt(false);
  }

  function removeDebt(index: number) {
    setForm((f) => ({ ...f, debts: (f.debts ?? []).filter((_, i) => i !== index) }));
  }

  // ── Goal management ──────────────────────────────────────────────────────

  function addGoal() {
    const errs: { description?: string; target_amount?: string } = {};
    if (!newGoal.description.trim()) errs.description = "Description required";
    if (newGoal.target_amount <= 0) errs.target_amount = "Target must be greater than 0";
    if (Object.keys(errs).length) { setGoalErrors(errs); return; }
    setForm((f) => ({ ...f, goals: [...(f.goals ?? []), { ...newGoal }] }));
    setNewGoal(BLANK_GOAL);
    setGoalErrors({});
    setAddingGoal(false);
  }

  function removeGoal(index: number) {
    setForm((f) => ({ ...f, goals: (f.goals ?? []).filter((_, i) => i !== index) }));
  }

  // ── Life events ──────────────────────────────────────────────────────────

  function toggleLifeEvent(value: string) {
    setForm((f) => {
      const current = f.recent_life_events ?? [];
      const updated = current.includes(value)
        ? current.filter((e) => e !== value)
        : [...current, value];
      return { ...f, recent_life_events: updated };
    });
  }

  // ── Submit ───────────────────────────────────────────────────────────────

  function handleSubmit() {
    const nextErrors: { age?: string; monthly_income?: string } = {};
    if (form.age < 18) nextErrors.age = "Age must be at least 18.";
    if (form.monthly_income <= 0) nextErrors.monthly_income = "Monthly income must be greater than 0.";
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length === 0) onSubmit(form);
  }

  // ── Computed display values ───────────────────────────────────────────────

  const debtMinPayments = (form.debts ?? []).reduce((s, d) => s + (d.minimum_payment || 0), 0);
  const monthly_surplus = (form.monthly_income ?? 0) - (form.monthly_expenses ?? 0) - debtMinPayments;
  const savings_rate =
    form.monthly_income > 0
      ? ((monthly_surplus / form.monthly_income) * 100).toFixed(1)
      : "—";

  const net_worth =
    (form.savings ?? 0) +
    (form.investments ?? 0) +
    (form.property_value ?? 0) -
    (form.debts?.reduce((s, d) => s + (d.balance || 0), 0) ?? 0);

  const total_debt = form.debts?.reduce((s, d) => s + (d.balance || 0), 0) ?? 0;

  const priorityColors: Record<string, string> = {
    critical: "text-red-400 border-red-500/30 bg-red-500/5",
    high:     "text-amber-400 border-amber-500/30 bg-amber-500/5",
    medium:   "text-cyan-400 border-cyan-500/30 bg-cyan-500/5",
    low:      "text-gray-400 border-gray-700 bg-gray-800/50",
  };

  const activeLifeEvents = form.recent_life_events ?? [];
  const selectedTaxBracket = TAX_BRACKETS.find((b) => b.value === form.tax_bracket);

  return (
    <div className="bg-gray-900/60 border border-gray-800 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-gray-800">
        <div>
          <h2 className="text-sm font-semibold text-white font-ui">Financial Profile</h2>
          <p className="mt-0.5 text-xs text-gray-500 font-ui">
            <span className="text-amber-500">·</span> Enter your financial details for a complete AI analysis
          </p>
        </div>
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
              {formatMoney(Math.abs(net_worth)) || "$0"}
            </span>
          </span>
        </div>
      </div>

      <div className="p-5 space-y-6">
        {/* ── Personal ─────────────────────────────────────────────────── */}
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
              {errors.age && <p className="mt-1 text-xs text-red-400 font-ui">{errors.age}</p>}
            </div>
            <div className="col-span-2">
              <label className={label}>LOCATION (City, State)</label>
              <input
                type="text"
                value={form.location}
                onChange={(e) => setStr("location", e.target.value)}
                className={field}
                placeholder="Austin, TX"
                disabled={disabled}
              />
            </div>
          </div>
          <div>
            <label className={label}>EMPLOYMENT STATUS</label>
            <select
              value={form.employment_status ?? "full_time"}
              onChange={(e) => setStr("employment_status", e.target.value)}
              className={field}
              disabled={disabled}
            >
              {EMPLOYMENT_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* ── Income & Expenses ─────────────────────────────────────────── */}
        <div className={section}>
          <div className={sectionHeader}>
            <DollarSign size={10} />
            INCOME &amp; EXPENSES
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className={label}>MONTHLY GROSS INCOME</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 text-sm pointer-events-none">$</span>
                <input
                  type="number"
                  value={form.monthly_income}
                  onChange={(e) => setNum("monthly_income", e.target.value)}
                  className={`${field} pl-6`}
                  min={0}
                  disabled={disabled}
                  placeholder="6000"
                />
              </div>
              {errors.monthly_income && (
                <p className="mt-1 text-xs text-red-400 font-ui">{errors.monthly_income}</p>
              )}
            </div>
            <div>
              <label className={label}>MONTHLY TOTAL EXPENSES</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 text-sm pointer-events-none">$</span>
                <input
                  type="number"
                  value={form.monthly_expenses}
                  onChange={(e) => setNum("monthly_expenses", e.target.value)}
                  className={`${field} pl-6`}
                  min={0}
                  disabled={disabled}
                  placeholder="4000"
                />
              </div>
            </div>
          </div>
          {/* Surplus bar */}
          {form.monthly_income > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-1">
                <div className="flex-1 h-1 bg-gray-800 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      monthly_surplus < 0
                        ? "bg-red-500"
                        : form.monthly_expenses / form.monthly_income > 0.9
                        ? "bg-red-500"
                        : form.monthly_expenses / form.monthly_income > 0.7
                        ? "bg-amber-500"
                        : "bg-emerald-500"
                    }`}
                    style={{ width: `${Math.min((form.monthly_expenses / form.monthly_income) * 100, 100)}%` }}
                  />
                </div>
                <span className="text-[10px] font-jet text-gray-600">
                  {((form.monthly_expenses / form.monthly_income) * 100).toFixed(0)}% expenses
                </span>
              </div>
              {debtMinPayments > 0 && (
                <p className="text-[10px] font-jet text-gray-700">
                  + ${debtMinPayments.toLocaleString()}/mo debt payments →{" "}
                  <span className={monthly_surplus >= 0 ? "text-emerald-400/70" : "text-red-400/70"}>
                    ${monthly_surplus.toLocaleString()} surplus
                  </span>
                </p>
              )}
            </div>
          )}
        </div>

        {/* ── Assets ───────────────────────────────────────────────────── */}
        <div className={section}>
          <div className={sectionHeader}>
            <TrendingUp size={10} />
            ASSETS
          </div>
          <div className="grid grid-cols-3 gap-3">
            <DollarInput label="SAVINGS" value={form.savings} onChange={(v) => setForm((f) => ({ ...f, savings: v }))} disabled={disabled} placeholder="15000" />
            <DollarInput label="INVESTMENTS" value={form.investments} onChange={(v) => setForm((f) => ({ ...f, investments: v }))} disabled={disabled} placeholder="5000" />
            <DollarInput label="PROPERTY VALUE" value={form.property_value} onChange={(v) => setForm((f) => ({ ...f, property_value: v }))} disabled={disabled} placeholder="0" />
          </div>
        </div>

        {/* ── Debts ────────────────────────────────────────────────────── */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className={sectionHeader} style={{ margin: 0 }}>
              <Shield size={10} />
              DEBTS {form.debts && form.debts.length > 0 && <span className="text-amber-500">({form.debts.length})</span>}
            </div>
            {!addingDebt && !disabled && (
              <button
                type="button"
                onClick={() => setAddingDebt(true)}
                className="flex items-center gap-1.5 text-[10px] font-jet text-amber-400 hover:text-amber-300 transition-colors"
              >
                <Plus size={10} />
                ADD DEBT
              </button>
            )}
          </div>

          {/* Existing debts */}
          {form.debts && form.debts.length > 0 && (
            <div className="space-y-2 mb-3">
              {form.debts.map((d, i) => (
                <div key={i} className="flex items-center gap-3 bg-gray-800/50 border border-gray-700/50 rounded-lg px-3 py-2.5 group">
                  <div className="flex-1 grid grid-cols-4 gap-2">
                    <div>
                      <p className="text-[9px] text-gray-600 font-jet">TYPE</p>
                      <p className="text-xs text-gray-300 font-ui capitalize">{String(d.type).replace(/_/g, " ")}</p>
                    </div>
                    <div>
                      <p className="text-[9px] text-gray-600 font-jet">BALANCE</p>
                      <p className="text-xs text-red-400 font-jet">${Number(d.balance).toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-[9px] text-gray-600 font-jet">APR</p>
                      <p className="text-xs text-white font-jet">{Number(d.interest_rate).toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-[9px] text-gray-600 font-jet">MIN/MO</p>
                      <p className="text-xs text-gray-300 font-jet">${Number(d.minimum_payment).toLocaleString()}</p>
                    </div>
                  </div>
                  {!disabled && (
                    <button
                      type="button"
                      onClick={() => removeDebt(i)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity text-gray-600 hover:text-red-400"
                    >
                      <Trash2 size={12} />
                    </button>
                  )}
                </div>
              ))}
              {total_debt > 0 && (
                <div className="flex justify-end text-[10px] font-jet text-gray-600">
                  Total debt: <span className="text-red-400 ml-1">${total_debt.toLocaleString()}</span>
                  {debtMinPayments > 0 && (
                    <span className="ml-2">· Min payments: <span className="text-amber-400/70">${debtMinPayments.toLocaleString()}/mo</span></span>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Add debt form */}
          {addingDebt && (
            <div className="bg-gray-800/60 border border-amber-500/20 rounded-xl p-4 space-y-3">
              <p className="text-[10px] font-jet text-amber-400 tracking-widest">NEW DEBT</p>
              <div className="grid grid-cols-2 gap-3">
                <div className="col-span-2">
                  <label className="block text-[10px] font-jet text-gray-500 mb-1">TYPE</label>
                  <select
                    value={newDebt.type}
                    onChange={(e) => setNewDebt((d) => ({ ...d, type: e.target.value }))}
                    className={miniField}
                  >
                    {DEBT_TYPES.map((t) => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
                <MiniDollarInput
                  label="CURRENT BALANCE"
                  value={newDebt.balance}
                  onChange={(v) => { setNewDebt((d) => ({ ...d, balance: v })); setDebtErrors({}); }}
                  placeholder="5000"
                />
                <div>
                  <label className="block text-[10px] font-jet text-gray-500 mb-1">INTEREST RATE (APR %)</label>
                  <input
                    type="number"
                    value={newDebt.interest_rate || ""}
                    onChange={(e) => setNewDebt((d) => ({ ...d, interest_rate: parseFloat(e.target.value) || 0 }))}
                    className={miniField}
                    min={0}
                    max={100}
                    step={0.1}
                    placeholder="5.5"
                  />
                </div>
                <MiniDollarInput
                  label="MINIMUM MONTHLY PAYMENT"
                  value={newDebt.minimum_payment}
                  onChange={(v) => setNewDebt((d) => ({ ...d, minimum_payment: v }))}
                  placeholder="150"
                />
              </div>
              {debtErrors.balance && (
                <p className="text-xs text-red-400 font-ui">{debtErrors.balance}</p>
              )}
              <div className="flex gap-2 pt-1">
                <button
                  type="button"
                  onClick={addDebt}
                  className="flex-1 bg-amber-500 hover:bg-amber-400 text-gray-950 font-semibold text-xs py-2 rounded-lg transition-colors font-ui"
                >
                  Add Debt
                </button>
                <button
                  type="button"
                  onClick={() => { setAddingDebt(false); setNewDebt(BLANK_DEBT); setDebtErrors({}); }}
                  className="px-4 bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs py-2 rounded-lg transition-colors font-ui"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {!addingDebt && (!form.debts || form.debts.length === 0) && (
            <button
              type="button"
              onClick={() => !disabled && setAddingDebt(true)}
              disabled={disabled}
              className="w-full border border-dashed border-gray-700 hover:border-amber-500/40 rounded-xl py-4 text-[10px] font-jet text-gray-600 hover:text-amber-500/60 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              + Add a debt (credit card, student loan, mortgage…)
            </button>
          )}
        </div>

        {/* ── Goals ────────────────────────────────────────────────────── */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className={sectionHeader} style={{ margin: 0 }}>
              <Target size={10} />
              FINANCIAL GOALS {form.goals && form.goals.length > 0 && <span className="text-amber-500">({form.goals.length})</span>}
            </div>
            {!addingGoal && !disabled && (
              <button
                type="button"
                onClick={() => setAddingGoal(true)}
                className="flex items-center gap-1.5 text-[10px] font-jet text-amber-400 hover:text-amber-300 transition-colors"
              >
                <Plus size={10} />
                ADD GOAL
              </button>
            )}
          </div>

          {/* Existing goals */}
          {form.goals && form.goals.length > 0 && (
            <div className="space-y-2 mb-3">
              {form.goals.map((g, i) => {
                const desc = (g as { description?: string; name?: string }).description ?? (g as { name?: string }).name ?? "Goal";
                const priority = g.priority ?? "medium";
                const timelineYears = (g.timeline_months / 12).toFixed(1);
                return (
                  <div key={i} className="flex items-center gap-3 bg-gray-800/50 border border-gray-700/50 rounded-lg px-3 py-2.5 group">
                    <div className="flex-1 grid grid-cols-3 gap-2">
                      <div className="col-span-3 sm:col-span-1">
                        <p className="text-[9px] text-gray-600 font-jet">GOAL</p>
                        <p className="text-xs text-gray-200 font-ui leading-snug">{desc}</p>
                      </div>
                      <div>
                        <p className="text-[9px] text-gray-600 font-jet">TARGET</p>
                        <p className="text-xs text-amber-400 font-jet">${Number(g.target_amount).toLocaleString()}</p>
                      </div>
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className="text-[9px] text-gray-600 font-jet">TIMELINE</p>
                          <p className="text-xs text-white font-jet">{g.timeline_months}mo ({timelineYears}yr)</p>
                        </div>
                        <span className={`text-[9px] font-jet px-1.5 py-0.5 rounded border shrink-0 mt-0.5 ${priorityColors[priority] ?? priorityColors.medium}`}>
                          {priority}
                        </span>
                      </div>
                    </div>
                    {!disabled && (
                      <button
                        type="button"
                        onClick={() => removeGoal(i)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity text-gray-600 hover:text-red-400"
                      >
                        <Trash2 size={12} />
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {/* Add goal form */}
          {addingGoal && (
            <div className="bg-gray-800/60 border border-amber-500/20 rounded-xl p-4 space-y-3">
              <p className="text-[10px] font-jet text-amber-400 tracking-widest">NEW GOAL</p>
              <div>
                <label className="block text-[10px] font-jet text-gray-500 mb-1">DESCRIPTION</label>
                <input
                  type="text"
                  value={newGoal.description}
                  onChange={(e) => { setNewGoal((g) => ({ ...g, description: e.target.value })); setGoalErrors({}); }}
                  className={miniField}
                  placeholder="e.g. Emergency fund, Down payment, Retire at 60…"
                />
                {goalErrors.description && (
                  <p className="mt-1 text-xs text-red-400 font-ui">{goalErrors.description}</p>
                )}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <MiniDollarInput
                  label="TARGET AMOUNT"
                  value={newGoal.target_amount}
                  onChange={(v) => { setNewGoal((g) => ({ ...g, target_amount: v })); setGoalErrors({}); }}
                  placeholder="20000"
                />
                <div>
                  <label className="block text-[10px] font-jet text-gray-500 mb-1">TIMELINE (MONTHS)</label>
                  <input
                    type="number"
                    value={newGoal.timeline_months || ""}
                    onChange={(e) => setNewGoal((g) => ({ ...g, timeline_months: parseInt(e.target.value) || 12 }))}
                    className={miniField}
                    min={1}
                    max={600}
                    placeholder="24"
                  />
                  {newGoal.timeline_months > 0 && (
                    <p className="text-[9px] font-jet text-gray-700 mt-0.5">
                      = {(newGoal.timeline_months / 12).toFixed(1)} years
                    </p>
                  )}
                </div>
              </div>
              {goalErrors.target_amount && (
                <p className="text-xs text-red-400 font-ui">{goalErrors.target_amount}</p>
              )}
              <div>
                <label className="block text-[10px] font-jet text-gray-500 mb-2">PRIORITY</label>
                <div className="grid grid-cols-4 gap-1.5">
                  {GOAL_PRIORITIES.map((p) => (
                    <button
                      key={p.value}
                      type="button"
                      onClick={() => setNewGoal((g) => ({ ...g, priority: p.value as Goal["priority"] }))}
                      className={`text-[10px] font-jet py-1.5 rounded-lg border transition-all ${
                        newGoal.priority === p.value
                          ? `${p.color} border-current bg-current/10`
                          : "text-gray-600 border-gray-700 hover:border-gray-600"
                      }`}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex gap-2 pt-1">
                <button
                  type="button"
                  onClick={addGoal}
                  className="flex-1 bg-amber-500 hover:bg-amber-400 text-gray-950 font-semibold text-xs py-2 rounded-lg transition-colors font-ui"
                >
                  Add Goal
                </button>
                <button
                  type="button"
                  onClick={() => { setAddingGoal(false); setNewGoal(BLANK_GOAL); setGoalErrors({}); }}
                  className="px-4 bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs py-2 rounded-lg transition-colors font-ui"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {!addingGoal && (!form.goals || form.goals.length === 0) && (
            <button
              type="button"
              onClick={() => !disabled && setAddingGoal(true)}
              disabled={disabled}
              className="w-full border border-dashed border-gray-700 hover:border-amber-500/40 rounded-xl py-4 text-[10px] font-jet text-gray-600 hover:text-amber-500/60 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              + Add a goal (emergency fund, home, retirement…)
            </button>
          )}
        </div>

        {/* ── Risk Profile ─────────────────────────────────────────────── */}
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
                  form.risk_tolerance === opt.value ? opt.activeColor : opt.color
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
              <span className="text-xs font-jet text-amber-400">{form.investment_horizon} yrs</span>
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
            <div className="flex justify-between text-[9px] font-jet text-gray-700 mt-0.5">
              <span>1 yr</span><span>Short-term</span><span>Long-term</span><span>50 yrs</span>
            </div>
          </div>
        </div>

        {/* ── Tax Bracket ──────────────────────────────────────────────── */}
        <div>
          <div className={sectionHeader}>
            <Briefcase size={10} />
            TAX BRACKET
            <span className="text-gray-700 font-jet text-[9px] normal-case tracking-normal ml-1">(helps Tax Intelligence agent)</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {TAX_BRACKETS.map((b) => (
              <button
                key={b.value}
                type="button"
                onClick={() =>
                  setForm((f) => ({
                    ...f,
                    tax_bracket: f.tax_bracket === b.value ? undefined : b.value,
                  }))
                }
                disabled={disabled}
                className={`rounded-lg px-3 py-2 text-left border transition-all disabled:opacity-40 ${
                  form.tax_bracket === b.value
                    ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-400"
                    : "border-gray-700 hover:border-gray-600 text-gray-500"
                }`}
              >
                <p className="text-xs font-jet font-semibold">{(b.value * 100).toFixed(0)}%</p>
                <p className="text-[9px] font-ui text-gray-600 mt-0.5 leading-tight">{b.label.split("—")[1]?.trim()}</p>
              </button>
            ))}
          </div>
          {form.tax_bracket && (
            <p className="text-[10px] font-jet text-emerald-400/70 mt-2">
              {selectedTaxBracket?.label}
            </p>
          )}
          {!form.tax_bracket && (
            <p className="text-[10px] font-jet text-gray-700 mt-2">
              Not selected — agent will estimate from income
            </p>
          )}
        </div>

        {/* ── Life Events ──────────────────────────────────────────────── */}
        <div>
          <div className={sectionHeader}>
            <Target size={10} />
            RECENT LIFE EVENTS
            <span className="text-gray-700 font-jet text-[9px] normal-case tracking-normal ml-1">(informs Life Event agent)</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {LIFE_EVENTS.map((evt) => {
              const isActive = activeLifeEvents.includes(evt.value);
              return (
                <button
                  key={evt.value}
                  type="button"
                  onClick={() => !disabled && toggleLifeEvent(evt.value)}
                  disabled={disabled}
                  className={`rounded-lg px-3 py-2 text-left border transition-all text-xs font-ui disabled:opacity-40 ${
                    isActive
                      ? "border-cyan-500/50 bg-cyan-500/10 text-cyan-300"
                      : "border-gray-700/60 hover:border-gray-600 text-gray-500"
                  }`}
                >
                  {evt.label}
                </button>
              );
            })}
          </div>
          {activeLifeEvents.length > 0 && (
            <p className="text-[10px] font-jet text-cyan-400/60 mt-2">
              {activeLifeEvents.length} event{activeLifeEvents.length !== 1 ? "s" : ""} selected
            </p>
          )}
        </div>

        {/* ── Credit Score Hint (optional) ──────────────────────────────── */}
        <CreditScoreSection
          value={form.credit_score}
          onChange={(v) => setForm((f) => ({ ...f, credit_score: v }))}
          disabled={disabled}
        />

        {/* ── Submit ───────────────────────────────────────────────────── */}
        <button
          type="button"
          onClick={handleSubmit}
          disabled={disabled}
          className="w-full bg-amber-500 hover:bg-amber-400 active:bg-amber-600 disabled:bg-gray-800 disabled:cursor-not-allowed text-gray-950 disabled:text-gray-600 font-semibold py-3 rounded-xl transition-colors text-sm font-ui tracking-wide flex items-center justify-center gap-2"
        >
          {disabled ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-gray-600 border-t-transparent rounded-full animate-spin" />
              Analyzing…
            </>
          ) : (
            <>
              Run Analysis →
              {(form.debts?.length ?? 0) > 0 && (
                <span className="text-xs text-gray-950/60 ml-1">{form.debts?.length} debt{(form.debts?.length ?? 0) !== 1 ? "s" : ""}</span>
              )}
              {(form.goals?.length ?? 0) > 0 && (
                <span className="text-xs text-gray-950/60">{form.goals?.length} goal{(form.goals?.length ?? 0) !== 1 ? "s" : ""}</span>
              )}
              {form.tax_bracket && (
                <span className="text-xs text-gray-950/60">{(form.tax_bracket * 100).toFixed(0)}% bracket</span>
              )}
            </>
          )}
        </button>
      </div>
    </div>
  );
}

function CreditScoreSection({
  value, onChange, disabled,
}: { value?: number; onChange: (v: number | undefined) => void; disabled?: boolean }) {
  const [expanded, setExpanded] = useState(false);
  // Local slider value tracks position independently of whether a score is "set"
  const [sliderVal, setSliderVal] = useState(value ?? 700);

  // Sync slider position if initialValues changes (demo persona load)
  useEffect(() => {
    if (value != null) setSliderVal(value);
  }, [value]);

  const scoreColor =
    !value ? "text-gray-600" :
    value >= 750 ? "text-emerald-400" :
    value >= 670 ? "text-amber-400" :
    value >= 580 ? "text-orange-400" :
    "text-red-400";

  const scoreLabel =
    !value ? "Not provided" :
    value >= 750 ? "Excellent" :
    value >= 670 ? "Good" :
    value >= 580 ? "Fair" :
    "Poor";

  function handleSliderChange(v: number) {
    setSliderVal(v);
    onChange(v);
  }

  return (
    <div className="border border-gray-800 rounded-xl overflow-hidden">
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-gray-800/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-jet text-gray-600 tracking-widest">CREDIT SCORE HINT</span>
          <span className="text-[10px] font-jet text-gray-700">(optional)</span>
          {value != null && (
            <span className={`text-[10px] font-jet ${scoreColor}`}>
              {value} — {scoreLabel}
            </span>
          )}
        </div>
        {expanded ? <ChevronUp size={12} className="text-gray-600" /> : <ChevronDown size={12} className="text-gray-600" />}
      </button>

      {expanded && (
        <div className="px-4 pb-4 border-t border-gray-800 bg-gray-900/30">
          <p className="text-[10px] text-gray-600 font-ui mt-3 mb-3 leading-relaxed">
            Your approximate credit score helps the Credit Intelligence agent give better optimization advice.
            Leave blank if unknown — the agent will estimate from your profile.
          </p>
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <input
                type="range"
                min={300}
                max={850}
                value={sliderVal}
                onChange={(e) => handleSliderChange(parseInt(e.target.value))}
                className="w-full"
                disabled={disabled}
              />
              <div className="flex justify-between text-[9px] font-jet text-gray-700 mt-0.5">
                <span>300</span><span>Poor</span><span>Fair</span><span>Good</span><span>850</span>
              </div>
            </div>
            <div className="text-right min-w-[80px]">
              <p className={`text-lg font-jet font-bold ${value != null ? scoreColor : "text-gray-600"}`}>
                {value ?? sliderVal}
              </p>
              <p className={`text-[10px] font-jet ${scoreColor}`}>{scoreLabel}</p>
            </div>
          </div>
          <div className="flex gap-3 mt-2">
            {value == null && (
              <button
                type="button"
                onClick={() => onChange(sliderVal)}
                className="text-[10px] font-jet text-amber-400 hover:text-amber-300 transition-colors"
              >
                Use {sliderVal}
              </button>
            )}
            {value != null && (
              <button
                type="button"
                onClick={() => { onChange(undefined); setSliderVal(700); }}
                className="text-[10px] font-jet text-gray-600 hover:text-gray-400 transition-colors"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
