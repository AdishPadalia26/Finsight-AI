"use client";

import { ShieldCheck, RefreshCw, AlertTriangle } from "lucide-react";

interface Props {
  scores: Record<string, unknown>;
}

const SCENARIO_META: Record<
  string,
  { label: string; detail: string; icon: string }
> = {
  JOB_LOSS: { label: "Job Loss", detail: "6 months income disruption", icon: "💼" },
  MARKET_CRASH: { label: "Market Crash", detail: "-30% portfolio value", icon: "📉" },
  MEDICAL_EMERGENCY: { label: "Medical Emergency", detail: "$50k unexpected expense", icon: "🏥" },
  RATE_SPIKE: { label: "Rate Spike", detail: "+3% interest rate increase", icon: "📈" },
  INFLATION_SPIKE: { label: "Inflation Spike", detail: "+5% cost of living surge", icon: "💸" },
};

function ScoreBar({ score }: { score: number }) {
  const pct = (score / 10) * 100;
  const color =
    score >= 8 ? "bg-emerald-400" : score >= 6 ? "bg-amber-400" : "bg-red-400";
  return (
    <div className="flex items-center gap-2 mt-2">
      <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="text-[9px] font-jet text-gray-600">/10</span>
    </div>
  );
}

function ScenarioCard({
  scenario,
  score,
}: {
  scenario: string;
  score: number;
}) {
  const meta = SCENARIO_META[scenario] ?? {
    label: scenario.replace(/_/g, " "),
    detail: "",
    icon: "⚡",
  };

  const scoreBg =
    score >= 8
      ? "bg-emerald-500/5 border-emerald-500/20"
      : score >= 6
      ? "bg-amber-500/5 border-amber-500/20"
      : "bg-red-500/5 border-red-500/20";

  const scoreColor =
    score >= 8 ? "text-emerald-400" : score >= 6 ? "text-amber-400" : "text-red-400";

  return (
    <div className={`rounded-xl border p-4 ${scoreBg}`}>
      <div className="flex items-start justify-between mb-2">
        <div>
          <div className="flex items-center gap-1.5 mb-0.5">
            <span className="text-base">{meta.icon}</span>
            <span className="text-xs font-semibold text-white font-ui">{meta.label}</span>
          </div>
          <p className="text-[10px] text-gray-600 font-ui">{meta.detail}</p>
        </div>
        <span className={`text-2xl font-jet font-bold ${scoreColor}`}>{score}</span>
      </div>
      <ScoreBar score={score} />
    </div>
  );
}

export default function StressTestDashboard({ scores }: Props) {
  if (!scores || Object.keys(scores).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-sm text-gray-600 font-ui">
        Stress test data not available
      </div>
    );
  }

  const scenarioScores = (scores.scores as Record<string, number>) ?? {};
  const status = (scores.status as string) ?? "";
  const iterations = (scores.iterations as number) ?? 1;
  const vulnerabilities = (scores.vulnerabilities as string[]) ?? [];

  const isApproved = status.includes("APPROVED");
  const wasRevised = status.includes("REVISED") || iterations > 1;
  const allScores = Object.values(scenarioScores);
  const lowestScore = allScores.length > 0 ? Math.min(...allScores) : 0;
  const avgScore =
    allScores.length > 0
      ? (allScores.reduce((a, b) => a + b, 0) / allScores.length).toFixed(1)
      : "—";

  return (
    <div className="space-y-5 animate-fade-in">
      {/* Verdict banner */}
      <div
        className={`rounded-xl border p-4 flex items-center gap-3 ${
          isApproved
            ? wasRevised
              ? "bg-amber-500/8 border-amber-500/25"
              : "bg-emerald-500/8 border-emerald-500/25"
            : "bg-red-500/8 border-red-500/25"
        }`}
      >
        {isApproved ? (
          <ShieldCheck
            size={20}
            className={wasRevised ? "text-amber-400" : "text-emerald-400"}
          />
        ) : (
          <AlertTriangle size={20} className="text-red-400" />
        )}
        <div className="flex-1">
          <p
            className={`text-sm font-semibold font-jet ${
              isApproved
                ? wasRevised
                  ? "text-amber-300"
                  : "text-emerald-300"
                : "text-red-300"
            }`}
          >
            {wasRevised ? "PLAN REVISED — APPROVED" : status.replace(/_/g, " — ")}
          </p>
          {wasRevised && iterations > 1 && (
            <p className="text-[10px] text-gray-500 font-ui mt-0.5">
              Revised after {iterations - 1} Critic iteration
              {iterations > 2 ? "s" : ""}
            </p>
          )}
        </div>
        <div className="text-right">
          <p className="text-[9px] font-jet text-gray-600 tracking-widest">AVG SCORE</p>
          <p className="text-lg font-jet font-bold text-white">{avgScore}</p>
        </div>
      </div>

      {/* Revision loop visualization */}
      {wasRevised && iterations > 1 && (
        <div className="flex items-center gap-1.5 text-[10px] font-jet text-gray-600 bg-gray-900/60 border border-gray-800 rounded-lg px-3 py-2">
          <RefreshCw size={10} className="text-amber-500" />
          <span className="text-amber-500">Critic</span>
          <span>→</span>
          <span>Budget Architect</span>
          <span>→</span>
          <span>Investment Strategist</span>
          <span>→</span>
          <span className="text-amber-500">Critic</span>
          <span className="ml-auto text-amber-500">×{iterations - 1}</span>
        </div>
      )}

      {/* Scenario cards */}
      {Object.keys(scenarioScores).length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-3">
            RESILIENCE SCORES
          </p>
          <div className="grid grid-cols-2 gap-2.5">
            {Object.entries(scenarioScores).map(([scenario, score]) => (
              <ScenarioCard key={scenario} scenario={scenario} score={score} />
            ))}
          </div>
        </div>
      )}

      {/* Low score warning */}
      {lowestScore < 6 && lowestScore > 0 && (
        <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-3">
          <p className="text-[9px] font-jet text-red-400 tracking-widest mb-1.5">
            VULNERABILITY DETECTED
          </p>
          <p className="text-xs text-red-300/80 font-ui">
            One or more scenarios scored below 6/10. Review the revised plan for
            mitigation strategies.
          </p>
        </div>
      )}

      {/* Vulnerabilities */}
      {vulnerabilities.length > 0 && (
        <div>
          <p className="text-[9px] font-jet text-gray-600 tracking-widest mb-2">
            KEY VULNERABILITIES
          </p>
          <ul className="space-y-1.5">
            {vulnerabilities.slice(0, 4).map((v, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-gray-400 font-ui">
                <span className="text-amber-500 shrink-0 mt-0.5">·</span>
                {v}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
