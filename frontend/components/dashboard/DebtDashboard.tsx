"use client";

import { displayText } from "@/lib/display";

interface SimResult {
  months_to_debt_free: number;
  total_interest_paid: number;
  interest_saved_vs_minimum: number;
  payoff_order?: { type: string; month: number; original_balance: number }[];
  minimum_only_months?: number;
  minimum_only_interest?: number;
}

interface Props {
  debt: Record<string, unknown>;
}

function CompareBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = max > 0 ? Math.min(100, (value / max) * 100) : 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <span className="text-[9px] font-jet text-gray-600">{label}</span>
        <span className="text-[10px] font-jet text-white">{value} mo</span>
      </div>
      <div className="w-full bg-gray-800 rounded-full h-2">
        <div className="h-2 rounded-full" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

export default function DebtDashboard({ debt }: Props) {
  if (!debt || Object.keys(debt).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-600 font-ui">
        Debt analysis not available
      </div>
    );
  }

  const method = String(debt.recommended_method ?? "—");
  const totalDebt = Number(debt.total_debt_balance ?? 0);
  const extraMonthly = Number(debt.extra_monthly_modeled ?? 0);
  const sims = (debt.simulations as Record<string, SimResult>) ?? {};
  const avalanche = sims.avalanche;
  const snowball = sims.snowball;
  const minOnly = sims.minimum_only;
  const explanation = String(debt.strategy_explanation ?? debt.payoff_timeline_narrative ?? "");
  const tipsRaw = debt.behavioral_tips;
  const tips: unknown[] = Array.isArray(tipsRaw) ? tipsRaw : [];
  const keyFinding = displayText(debt.key_finding);

  const selected = sims[method] ?? avalanche;
  const maxMonths = Math.max(
    minOnly?.months_to_debt_free ?? 0,
    avalanche?.months_to_debt_free ?? 0,
    snowball?.months_to_debt_free ?? 0,
    1
  );

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Summary strip */}
      <div className="grid grid-cols-3 gap-2.5">
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3">
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-1.5">TOTAL DEBT</p>
          <p className="text-lg font-jet text-red-400">${totalDebt.toLocaleString()}</p>
        </div>
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3">
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-1.5">STRATEGY</p>
          <p className="text-sm font-jet text-amber-400 capitalize">{method}</p>
        </div>
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3">
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-1.5">EXTRA / MONTH</p>
          <p className="text-lg font-jet text-emerald-400">${extraMonthly.toLocaleString()}</p>
        </div>
      </div>

      {/* Interest saved highlight */}
      {selected && selected.interest_saved_vs_minimum > 0 && (
        <div className="bg-emerald-500/8 border border-emerald-500/20 rounded-xl p-4 text-center">
          <p className="text-[10px] text-gray-500 font-jet mb-1">INTEREST SAVED VS. MINIMUM-ONLY PATH</p>
          <p className="text-2xl font-display text-emerald-400">
            ${selected.interest_saved_vs_minimum.toLocaleString()}
          </p>
          <p className="text-xs text-gray-600 font-ui mt-0.5">
            {selected.months_to_debt_free} months to debt-free vs. {minOnly?.months_to_debt_free ?? "—"} months minimum-only
          </p>
        </div>
      )}

      {/* Strategy comparison bars */}
      {(avalanche || snowball || minOnly) && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">PAYOFF TIMELINE COMPARISON</p>
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-4 space-y-3">
            {minOnly && (
              <CompareBar label="MINIMUM ONLY" value={minOnly.months_to_debt_free} max={maxMonths} color="#EF4444" />
            )}
            {snowball && (
              <CompareBar label="SNOWBALL" value={snowball.months_to_debt_free} max={maxMonths} color="#F59E0B" />
            )}
            {avalanche && (
              <CompareBar label="AVALANCHE" value={avalanche.months_to_debt_free} max={maxMonths} color="#10B981" />
            )}
          </div>
        </div>
      )}

      {/* Payoff order */}
      {selected?.payoff_order && selected.payoff_order.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">PAYOFF ORDER</p>
          <div className="space-y-1">
            {selected.payoff_order.map((item, i) => (
              <div key={i} className="flex items-center gap-3 bg-gray-900/60 border border-gray-800 rounded-lg px-3 py-2">
                <span className="text-[10px] font-jet text-amber-500 w-4 text-center">{i + 1}</span>
                <span className="text-xs text-white font-ui capitalize">{item.type?.replace(/_/g, " ")}</span>
                <span className="ml-auto text-[10px] text-gray-500 font-jet">month {item.month}</span>
                <span className="text-[10px] text-gray-600 font-jet">${item.original_balance?.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Strategy explanation */}
      {explanation && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">STRATEGY RATIONALE</p>
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-3">
            <p className="text-xs text-gray-400 font-ui leading-relaxed">{explanation}</p>
          </div>
        </div>
      )}

      {/* Key finding */}
      {keyFinding && (
        <div className="bg-amber-500/5 border border-amber-500/15 rounded-xl p-3">
          <p className="text-[9px] font-jet text-amber-500/60 mb-1">KEY FINDING</p>
          <p className="text-xs text-amber-200 font-ui">{keyFinding}</p>
        </div>
      )}

      {/* Behavioral tips */}
      {tips.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">BEHAVIORAL TIPS</p>
          <ol className="space-y-2">
            {tips.map((tip, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <span className="text-[10px] font-jet text-amber-500 shrink-0 mt-0.5">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <p className="text-xs text-gray-400 font-ui leading-relaxed">{displayText(tip)}</p>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
