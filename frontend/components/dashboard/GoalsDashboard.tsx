"use client";

import { displayText } from "@/lib/display";

interface GoalData {
  description: unknown;
  target_amount: number;
  timeline_months: number;
  required_monthly_contribution: number;
  feasibility_score: number;
  recommended_vehicle_category: unknown;
  risk_flag: string;
  milestone_balances?: { month?: number; balance?: number; step?: unknown; timeframe?: unknown }[];
}

interface Props {
  goals: Record<string, unknown>;
}

function FeasibilityBar({ score }: { score: number }) {
  const color =
    score >= 80 ? "#10B981" :
    score >= 50 ? "#F59E0B" :
    "#EF4444";
  return (
    <div className="w-full bg-gray-800 rounded-full h-1.5 mt-1">
      <div
        className="h-1.5 rounded-full transition-all duration-700"
        style={{ width: `${Math.min(100, score)}%`, background: color }}
      />
    </div>
  );
}

function GoalCard({ goal }: { goal: GoalData }) {
  const flagColor =
    goal.risk_flag === "FEASIBLE" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" :
    goal.risk_flag === "AT_RISK" ? "bg-amber-500/10 text-amber-400 border-amber-500/20" :
    "bg-red-500/10 text-red-400 border-red-500/20";

  const years = (goal.timeline_months / 12).toFixed(1);

  return (
    <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 space-y-3">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm text-white font-ui font-medium leading-snug">{displayText(goal.description)}</p>
        <span className={`text-[9px] font-jet px-2 py-0.5 rounded border shrink-0 ${flagColor}`}>
          {goal.risk_flag?.replace("_", " ")}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div>
          <p className="text-[9px] text-gray-600 font-jet">TARGET</p>
          <p className="text-sm font-jet text-white">${goal.target_amount?.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-[9px] text-gray-600 font-jet">TIMELINE</p>
          <p className="text-sm font-jet text-white">{goal.timeline_months} mo ({years} yr)</p>
        </div>
        <div>
          <p className="text-[9px] text-gray-600 font-jet">REQUIRED / MONTH</p>
          <p className="text-sm font-jet text-amber-400">${goal.required_monthly_contribution?.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-[9px] text-gray-600 font-jet">FEASIBILITY</p>
          <p className="text-sm font-jet text-white">{goal.feasibility_score?.toFixed(0)}%</p>
          <FeasibilityBar score={goal.feasibility_score ?? 0} />
        </div>
      </div>

      {Boolean(goal.recommended_vehicle_category) && (
        <div className="bg-indigo-500/5 border border-indigo-500/15 rounded-lg px-3 py-1.5">
          <p className="text-[9px] text-gray-600 font-jet mb-0.5">RECOMMENDED VEHICLE</p>
          <p className="text-xs text-indigo-300 font-ui">{displayText(goal.recommended_vehicle_category)}</p>
        </div>
      )}

      {goal.milestone_balances && goal.milestone_balances.length > 0 && (
        <div>
          <p className="text-[9px] text-gray-600 font-jet mb-1.5">MILESTONE PROJECTIONS</p>
          <div className="flex gap-2">
            {goal.milestone_balances.map((m, i) => (
              <div key={i} className="flex-1 text-center bg-gray-800 rounded-lg p-1.5">
                <p className="text-[8px] text-gray-600 font-jet">{m.month != null ? `mo ${m.month}` : displayText(m.timeframe)}</p>
                <p className="text-[10px] font-jet text-white">
                  {m.balance != null ? `$${m.balance.toLocaleString()}` : displayText(m.step)}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function GoalsDashboard({ goals }: Props) {
  if (!goals || Object.keys(goals).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-600 font-ui">
        Goal analysis not available
      </div>
    );
  }

  const computedRaw = goals.computed_goals;
  const computed: GoalData[] = Array.isArray(computedRaw) ? computedRaw : [];
  const cross = (goals.cross_goal_summary as Record<string, unknown>) ?? {};
  const fundingGap = Number(cross.funding_gap ?? 0);
  const totalRequired = Number(cross.total_required_monthly ?? 0);
  const available = Number(cross.available_monthly_for_goals ?? 0);

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Cross-goal summary strip */}
      <div className="grid grid-cols-3 gap-2.5">
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3">
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-1.5">TOTAL REQUIRED / MO</p>
          <p className="text-lg font-jet text-amber-400">${totalRequired.toLocaleString()}</p>
        </div>
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3">
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-1.5">AVAILABLE / MO</p>
          <p className="text-lg font-jet text-white">${available.toLocaleString()}</p>
        </div>
        <div className={`border rounded-xl p-3 ${fundingGap > 0 ? "bg-red-500/8 border-red-500/25" : "bg-emerald-500/8 border-emerald-500/25"}`}>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-1.5">FUNDING GAP</p>
          <p className={`text-lg font-jet ${fundingGap > 0 ? "text-red-400" : "text-emerald-400"}`}>
            {fundingGap > 0 ? `$${fundingGap.toLocaleString()}` : "None"}
          </p>
        </div>
      </div>

      {/* Conflict warning */}
      {fundingGap > 0 && (
        <div className="bg-amber-500/8 border border-amber-500/25 rounded-xl p-3">
          <p className="text-xs text-amber-300 font-ui">
            All goals simultaneously require <span className="font-semibold">${totalRequired.toLocaleString()}/mo</span> but
            only <span className="font-semibold">${available.toLocaleString()}/mo</span> is available.
            Consider extending lower-priority goal timelines or increasing income to close the ${fundingGap.toLocaleString()} gap.
          </p>
        </div>
      )}

      {/* Goal cards */}
      {computed.length > 0 ? (
        <div className="space-y-3">
          <p className="text-[9px] font-jet text-gray-600 tracking-widest">GOAL ANALYSIS</p>
          {computed.map((goal, i) => (
            <GoalCard key={i} goal={goal} />
          ))}
        </div>
      ) : (
        <div className="flex items-center justify-center h-32 text-sm text-gray-600 font-ui">
          No goals analyzed
        </div>
      )}
    </div>
  );
}
