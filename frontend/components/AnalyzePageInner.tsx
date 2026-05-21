"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { AlertTriangle, RotateCcw, Download } from "lucide-react";
import { useAnalysis } from "@/hooks/useAnalysis";
import DemoPersonaCards from "@/components/forms/DemoPersonaCards";
import FinancialProfileForm from "@/components/forms/FinancialProfileForm";
import AgentPipeline from "@/components/pipeline/AgentPipeline";
import OverviewDashboard from "@/components/dashboard/OverviewDashboard";
import BudgetDashboard from "@/components/dashboard/BudgetDashboard";
import InvestmentDashboard from "@/components/dashboard/InvestmentDashboard";
import GoalsDashboard from "@/components/dashboard/GoalsDashboard";
import DebtDashboard from "@/components/dashboard/DebtDashboard";
import TaxDashboard from "@/components/dashboard/TaxDashboard";
import AdviceDashboard from "@/components/dashboard/AdviceDashboard";
import StressTestDashboard from "@/components/dashboard/StressTestDashboard";
import ComplianceReport from "@/components/dashboard/ComplianceReport";
import ExplainabilityPanel from "@/components/dashboard/ExplainabilityPanel";
import ScenarioSimulator from "@/components/simulator/ScenarioSimulator";
import { fetchDemoPersona } from "@/lib/api";
import type { FinancialProfile } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type DashTab = "overview" | "budget" | "investment" | "goals" | "debt" | "tax" | "advice" | "stress" | "compliance";

const DASH_TABS: { id: DashTab; label: string }[] = [
  { id: "overview",    label: "Overview" },
  { id: "budget",      label: "Budget" },
  { id: "investment",  label: "Investment" },
  { id: "goals",       label: "Goals" },
  { id: "debt",        label: "Debt" },
  { id: "tax",         label: "Tax" },
  { id: "advice",      label: "Advice" },
  { id: "stress",      label: "Stress Test" },
  { id: "compliance",  label: "Compliance" },
];

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

function fallbackInvestment(report: Record<string, unknown>): Record<string, unknown> {
  const session = asRecord(report.session);
  const risk = String(session.risk_tolerance ?? "moderate");
  const allocation =
    risk === "conservative"
      ? { us_equities: 35, international_equities: 15, bonds: 35, cash: 10, alternatives: 5 }
      : risk === "aggressive"
      ? { us_equities: 60, international_equities: 25, bonds: 10, cash: 2, alternatives: 3 }
      : { us_equities: 50, international_equities: 20, bonds: 20, cash: 5, alternatives: 5 };
  return {
    allocation,
    risk_alignment: `Fallback allocation reflects a ${risk} profile.`,
    rationale: "Investment strategy was missing from the completed report.",
    account_optimization: "Use tax-advantaged retirement accounts for higher-growth assets.",
    rebalancing_guidance: "Review quarterly and rebalance when any asset class drifts more than 5%.",
    market_context: {},
    fallback: true,
  };
}

export default function AnalyzePageInner() {
  const searchParams = useSearchParams();
  const analysis = useAnalysis();
  const resultsRef = useRef<HTMLDivElement | null>(null);
  const autoDemoStarted = useRef(false);
  const [loadedProfile, setLoadedProfile] = useState<Record<string, unknown> | null>(null);
  const [activePersona, setActivePersona] = useState<string | null>(null);
  const [dashTab, setDashTab] = useState<DashTab>("overview");
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  const isRunning = analysis.status === "running";
  const isComplete = analysis.status === "complete";
  const isError = analysis.status === "error";
  const showPipeline = isRunning || isComplete || isError;
  const showDashboard = isComplete && analysis.result !== null;

  useEffect(() => {
    if (isComplete) {
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  }, [isComplete]);

  useEffect(() => {
    const demo = searchParams.get("demo");
    if (!demo || autoDemoStarted.current) return;
    if (!["alex", "jordan", "sam"].includes(demo)) return;
    autoDemoStarted.current = true;
    fetchDemoPersona(demo as "alex" | "jordan" | "sam")
      .then((data) => {
        const profile = data.profile ?? data;
        setLoadedProfile(profile);
        setActivePersona(demo);
        window.setTimeout(() => analysis.run({ profile }), 400);
      })
      .catch((err) => console.error(err));
  }, [analysis, searchParams]);

  function handlePersonaLoad(profile: Record<string, unknown>, personaId: string) {
    analysis.reset();
    setLoadedProfile(profile);
    setActivePersona(personaId);
  }

  function handleSubmit(profile: FinancialProfile) {
    const p = profile as unknown as Record<string, unknown>;
    setLoadedProfile(p);
    analysis.run({ profile: p });
  }

  function handleRetry() {
    if (loadedProfile) analysis.run({ profile: loadedProfile });
  }

  async function handleDownloadPdf() {
    const finalReport = analysis.result?.final_report;
    if (!finalReport) return;
    setDownloadingPdf(true);
    try {
      const resp = await fetch(`${API_BASE}/report/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          final_report: finalReport,
          session_id: analysis.result?.session_id ?? "session",
        }),
      });
      if (!resp.ok) throw new Error(`PDF generation failed: ${resp.status}`);
      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "finsight_report.pdf";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("PDF download error:", e);
    } finally {
      setDownloadingPdf(false);
    }
  }

  const result = analysis.result;
  const report = asRecord(result?.final_report);
  const overview    = asRecord(report.overview);
  const budgetData  = asRecord(report.budget ?? report.budget_recommendation);
  const invDataRaw  = asRecord(report.investment ?? report.investment_strategy);
  const invData     = Object.keys(invDataRaw).length > 0 ? invDataRaw : fallbackInvestment(report);
  const goalsData   = asRecord(report.goals ?? report.goal_roadmap);
  const debtData    = asRecord(report.debt ?? report.debt_roadmap);
  const taxData     = asRecord(report.tax ?? report.tax_opportunities);
  const adviceData  = asRecord(report.personalised_advice);
  const criticData  = asRecord(report.critic ?? result?.critic_scores);
  const stressBase  = asRecord(report.stress_tests);
  const stressData: Record<string, unknown> = stressBase.scenarios
    ? { ...stressBase, status: (criticData.status as string) ?? "", iterations: Number(criticData.revision_count ?? 0) + 1 }
    : asRecord(result?.critic_scores);
  const complianceData = asRecord(report.compliance ?? result?.compliance_audit);
  const budgetHealthScore = asRecord(budgetData.health_score);
  const healthScore  = Number(overview.health_score ?? budgetHealthScore.total ?? 0);
  const healthGrade  = String(overview.health_grade ?? (budgetData.health_score as Record<string, unknown>)?.grade ?? "—");
  const circumference = 2 * Math.PI * 44;
  const healthOffset  = circumference - (Math.max(0, Math.min(100, healthScore)) / 100) * circumference;

  return (
    <main className="min-h-screen bg-[#0A0F1E] pb-16">
      <section className="border-b border-gray-800/60 px-6 py-6">
        <div className="max-w-4xl mx-auto">
          <Link href="/" className="text-[10px] font-jet tracking-widest text-amber-500 hover:text-amber-400">
            BACK TO OVERVIEW
          </Link>
          <h1 className="mt-3 font-display text-4xl text-white">Financial Analysis</h1>
          <p className="mt-1 text-sm text-gray-500 font-ui">
            12-agent pipeline, real-time market context, and compliance guardrails.
          </p>
        </div>
      </section>

      <div className="max-w-4xl mx-auto px-4 pt-6 space-y-6">
        {!isRunning && !isComplete && (
          <DemoPersonaCards onLoad={handlePersonaLoad} activePersona={activePersona} disabled={isRunning} />
        )}
        {!isRunning && !isComplete && (
          <FinancialProfileForm initialValues={loadedProfile} onSubmit={handleSubmit} disabled={isRunning} />
        )}
        {isError && (
          <div className="bg-red-500/8 border border-red-500/25 rounded-2xl p-5">
            <div className="flex items-start gap-3">
              <AlertTriangle size={18} className="text-red-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-red-300 font-ui">Analysis failed</p>
                <p className="mt-1 text-xs text-red-300/80 font-ui">{analysis.error}</p>
              </div>
              <button onClick={handleRetry} disabled={!loadedProfile} className="inline-flex items-center gap-2 rounded-lg bg-amber-500 px-3 py-2 text-xs font-semibold text-gray-950 hover:bg-amber-400 disabled:opacity-40">
                <RotateCcw size={12} />Retry
              </button>
            </div>
          </div>
        )}
        {showPipeline && <AgentPipeline agents={analysis.agents} revisionCount={analysis.revisionCount} />}
        {showDashboard && (
          <div ref={resultsRef} className="scroll-mt-24 space-y-5">
            <div className="rounded-2xl border border-amber-500/15 bg-gray-900/50 p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-5">
                  <div className="relative h-28 w-28">
                    <svg viewBox="0 0 100 100" className="h-28 w-28">
                      <circle cx="50" cy="50" r="44" fill="none" stroke="#1f2937" strokeWidth="8" />
                      <circle cx="50" cy="50" r="44" fill="none" stroke="#f59e0b" strokeWidth="8" strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={healthOffset} className="progress-ring-circle" />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="font-display text-4xl text-white">{Math.round(healthScore)}</span>
                    </div>
                  </div>
                  <div>
                    <p className="text-[10px] font-jet tracking-[0.2em] text-gray-600">FINANCIAL HEALTH SCORE</p>
                    <p className="font-display text-5xl text-amber-400">{healthGrade}</p>
                    <p className="text-xs text-gray-500 font-ui">after compliance review</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <button onClick={() => { analysis.reset(); setLoadedProfile(null); setActivePersona(null); }} className="inline-flex items-center gap-2 rounded-xl border border-gray-700 px-4 py-2.5 text-xs font-semibold text-gray-300 hover:border-gray-500 hover:text-white transition-colors">
                    <RotateCcw size={14} />New Analysis
                  </button>
                  <button onClick={handleDownloadPdf} disabled={downloadingPdf} className="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-4 py-2.5 text-xs font-semibold text-gray-950 hover:bg-amber-400 disabled:opacity-50 transition-colors">
                    <Download size={14} />{downloadingPdf ? "Generating…" : "Download Report"}
                  </button>
                </div>
              </div>
            </div>
            <div className="flex overflow-x-auto border-b border-gray-800 bg-gray-900/40 rounded-t-2xl scrollbar-none">
              {DASH_TABS.map((tab) => (
                <button key={tab.id} onClick={() => setDashTab(tab.id)} className={`min-w-[80px] flex-1 text-xs py-3 font-ui transition-colors whitespace-nowrap ${dashTab === tab.id ? "text-amber-400 border-b-2 border-amber-500 bg-amber-500/5" : "text-gray-500 hover:text-gray-300"}`}>
                  {tab.label}
                </button>
              ))}
            </div>
            <div className="bg-gray-900/40 border border-gray-800 rounded-b-2xl rounded-tr-2xl p-5">
              {dashTab === "overview"   && <OverviewDashboard overview={overview} advice={adviceData} />}
              {dashTab === "budget"     && <BudgetDashboard budget={budgetData} />}
              {dashTab === "investment" && <InvestmentDashboard investment={invData} />}
              {dashTab === "goals"      && <GoalsDashboard goals={goalsData} />}
              {dashTab === "debt"       && <DebtDashboard debt={debtData} />}
              {dashTab === "tax"        && <TaxDashboard tax={taxData} />}
              {dashTab === "advice"     && <AdviceDashboard advice={adviceData} />}
              {dashTab === "stress"     && <StressTestDashboard scores={stressData} />}
              {dashTab === "compliance" && <ComplianceReport audit={complianceData} pipelineErrors={result?.pipeline_errors} />}
            </div>
            <ExplainabilityPanel agents={analysis.agents} />
            <ScenarioSimulator baseProfile={loadedProfile} disabled={isRunning} />
          </div>
        )}
      </div>
    </main>
  );
}
