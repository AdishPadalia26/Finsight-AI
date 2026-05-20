"use client";

import { displayText } from "@/lib/display";

interface Opportunity {
  name?: string;
  annual_savings_potential?: number;
  priority?: string;
  explanation?: string;
}

interface Props {
  tax: Record<string, unknown>;
}

function OpportunityCard({ opp, index }: { opp: Opportunity; index: number }) {
  const priorityColor: Record<string, string> = {
    high:   "bg-red-500/10 text-red-400 border-red-500/20",
    medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    low:    "bg-gray-700/30 text-gray-500 border-gray-700",
  };
  const priority = String(opp.priority ?? "medium").toLowerCase();
  const colorClass = priorityColor[priority] ?? priorityColor.medium;
  const title = displayText(opp.name) || displayText(opp) || `Opportunity ${index + 1}`;
  const explanation = displayText(opp.explanation);

  return (
    <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 space-y-2">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm text-white font-ui font-medium">{title}</p>
        <span className={`text-[9px] font-jet px-2 py-0.5 rounded border shrink-0 ${colorClass}`}>
          {(opp.priority ?? "medium").toUpperCase()}
        </span>
      </div>
      {opp.annual_savings_potential != null && (
        <p className="text-base font-jet text-emerald-400">
          Est. ${Number(opp.annual_savings_potential).toLocaleString()}/yr savings
        </p>
      )}
      {explanation && (
        <p className="text-xs text-gray-500 font-ui leading-relaxed">{explanation}</p>
      )}
    </div>
  );
}

export default function TaxDashboard({ tax }: Props) {
  if (!tax || Object.keys(tax).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-600 font-ui">
        Tax analysis not available
      </div>
    );
  }

  const precomp = (tax.precomputed_metrics as Record<string, unknown>) ?? {};
  const opportunitiesRaw = tax.tax_optimization_opportunities;
  const opportunities: Opportunity[] = Array.isArray(opportunitiesRaw) ? opportunitiesRaw : [];
  const retirementStrategy = displayText(tax.retirement_account_strategy);
  const hsaRec = displayText(tax.hsa_recommendation);
  const tlh = String(tax.tax_loss_harvesting ?? "");
  const totalSavings = Number(tax.total_annual_savings_potential ?? 0);
  const keyAction = displayText(tax.key_action);
  const deadlinesRaw = tax.deadline_reminders;
  const deadlines: unknown[] = Array.isArray(deadlinesRaw) ? deadlinesRaw : [];

  const limits = (precomp.contribution_limits_2025 as Record<string, number>) ?? {};
  const marginalBracket = Number(precomp.marginal_bracket_pct ?? 0);
  const effectiveRate = Number(precomp.effective_rate_estimate_pct ?? 0);
  const catchup = Boolean(precomp.catchup_contributions_eligible);
  const rothPreferred = Boolean((precomp.roth_vs_traditional as Record<string, unknown>)?.roth_preferred);

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Tax overview strip */}
      <div className="grid grid-cols-3 gap-2.5">
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3">
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-1.5">MARGINAL BRACKET</p>
          <p className="text-lg font-jet text-white">{marginalBracket.toFixed(0)}%</p>
          <p className="text-[9px] text-gray-600 font-ui mt-0.5">Federal — 2025</p>
        </div>
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3">
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-1.5">EFFECTIVE RATE EST.</p>
          <p className="text-lg font-jet text-white">{effectiveRate.toFixed(1)}%</p>
          <p className="text-[9px] text-gray-600 font-ui mt-0.5">Approximate</p>
        </div>
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3">
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-1.5">SAVINGS POTENTIAL</p>
          <p className="text-lg font-jet text-emerald-400">
            {totalSavings > 0 ? `$${totalSavings.toLocaleString()}/yr` : "—"}
          </p>
        </div>
      </div>

      {/* Contribution limits */}
      {Object.keys(limits).length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">2025 IRS CONTRIBUTION LIMITS</p>
          <div className="grid grid-cols-3 gap-2">
            {Object.entries(limits).map(([key, val]) => (
              <div key={key} className="bg-gray-900/60 border border-gray-800 rounded-lg p-2.5 text-center">
                <p className="text-[8px] text-gray-600 font-jet mb-1">{key.replace(/_/g, " ").toUpperCase()}</p>
                <p className="text-sm font-jet text-white">${Number(val).toLocaleString()}</p>
              </div>
            ))}
          </div>
          {catchup && (
            <p className="text-[10px] text-amber-400 font-jet mt-1.5">
              ★ Catch-up contributions available (age 50+)
            </p>
          )}
        </div>
      )}

      {/* Key action */}
      {keyAction && (
        <div className="bg-amber-500/5 border border-amber-500/15 rounded-xl p-4">
          <p className="text-[9px] font-jet text-amber-500/60 mb-1">HIGHEST-IMPACT ACTION</p>
          <p className="text-sm text-amber-200 font-ui font-medium">{keyAction}</p>
        </div>
      )}

      {/* Opportunities */}
      {opportunities.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">OPTIMIZATION OPPORTUNITIES</p>
          <div className="space-y-2">
            {opportunities.slice(0, 6).map((opp, i) => (
              <OpportunityCard key={i} opp={typeof opp === "object" && opp !== null ? opp : { name: displayText(opp) }} index={i} />
            ))}
          </div>
        </div>
      )}

      {/* Roth vs Traditional */}
      <div>
        <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">ROTH VS. TRADITIONAL</p>
        <div className={`border rounded-xl p-3 ${rothPreferred ? "bg-indigo-500/5 border-indigo-500/15" : "bg-gray-900/60 border-gray-800"}`}>
          <p className="text-xs text-gray-300 font-ui">
            <span className="font-semibold text-white">{rothPreferred ? "Roth Preferred" : "Traditional/Pre-Tax Preferred"}</span>
            {" — "}
            {String((precomp.roth_vs_traditional as Record<string, unknown>)?.rationale ?? "")}
          </p>
        </div>
      </div>

      {/* Retirement account strategy */}
      {retirementStrategy && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">RETIREMENT ACCOUNT STRATEGY</p>
          <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-3">
            <p className="text-xs text-gray-400 font-ui leading-relaxed">{retirementStrategy}</p>
          </div>
        </div>
      )}

      {/* HSA */}
      {hsaRec && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">HSA RECOMMENDATION</p>
          <div className="bg-green-500/5 border border-green-500/10 rounded-xl p-3">
            <p className="text-xs text-gray-400 font-ui leading-relaxed">{hsaRec}</p>
          </div>
        </div>
      )}

      {/* Deadlines */}
      {deadlines.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">UPCOMING TAX DEADLINES</p>
          <ul className="space-y-1">
            {deadlines.map((d, i) => (
              <li key={i} className="flex items-center gap-2 text-xs text-gray-500 font-ui">
                <span className="text-amber-500">▸</span>
                {displayText(d)}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
