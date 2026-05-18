"use client";

import { useState } from "react";
import { useAnalysis } from "@/hooks/useAnalysis";
import DemoPersonaCards from "@/components/forms/DemoPersonaCards";
import FinancialProfileForm from "@/components/forms/FinancialProfileForm";
import AgentPipeline from "@/components/pipeline/AgentPipeline";
import BudgetDashboard from "@/components/dashboard/BudgetDashboard";
import InvestmentDashboard from "@/components/dashboard/InvestmentDashboard";
import StressTestDashboard from "@/components/dashboard/StressTestDashboard";
import ComplianceReport from "@/components/dashboard/ComplianceReport";
import ExplainabilityPanel from "@/components/dashboard/ExplainabilityPanel";
import ScenarioSimulator from "@/components/simulator/ScenarioSimulator";
import type { FinancialProfile } from "@/lib/types";

type DashTab = "budget" | "investment" | "stress" | "compliance";

const DASH_TABS: { id: DashTab; label: string }[] = [
  { id: "budget", label: "Budget" },
  { id: "investment", label: "Investment" },
  { id: "stress", label: "Stress Test" },
  { id: "compliance", label: "Compliance" },
];

export default function AnalyzePage() {
  const analysis = useAnalysis();
  const [loadedProfile, setLoadedProfile] = useState<Record<string, unknown> | null>(null);
  const [activePersona, setActivePersona] = useState<string | null>(null);
  const [dashTab, setDashTab] = useState<DashTab>("budget");

  const isIdle = analysis.status === "idle";
  const isRunning = analysis.status === "running";
  const isComplete = analysis.status === "complete";
  const showPipeline = isRunning || isComplete;
  const showDashboard = isComplete && analysis.result !== null;

  function handlePersonaLoad(profile: Record<string, unknown>, personaId: string) {
    setLoadedProfile(profile);
    setActivePersona(personaId);
  }

  function handleSubmit(profile: FinancialProfile) {
    const p = profile as unknown as Record<string, unknown>;
    analysis.run({ profile: p });
  }

  function handleRerun(overrides: Record<string, number>) {
    if (!loadedProfile) return;
    analysis.run({
      profile: { ...loadedProfile, scenario_overrides: overrides },
    });
  }

  const report = (analysis.result?.final_report ?? {}) as Record<string, unknown>;
  const budgetData = (report.budget_recommendation ?? {}) as Record<string, unknown>;
  const investmentData = (report.investment_strategy ?? {}) as Record<string, unknown>;
  const stressData = (analysis.result?.critic_scores ?? {}) as Record<string, unknown>;
  const complianceData = (analysis.result?.compliance_audit ?? {}) as Record<string, unknown>;

  return (
    <main className="min-h-screen bg-[#0A0F1E] pb-16">
      {/* Page header */}
      <div className="border-b border-gray-800/60 px-6 py-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-sm font-semibold text-white font-ui">Financial Analysis</h1>
          <p className="text-xs text-gray-600 font-ui mt-0.5">
            12-agent pipeline · Real-time market data · Compliance guardrails
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 pt-6">
        {/* Demo persona cards — always visible */}
        <DemoPersonaCards
          onLoad={handlePersonaLoad}
          activePersona={activePersona}
          disabled={isRunning}
        />

        {/* Main layout */}
        {showDashboard ? (
          /* Split view when complete */
          <div className="grid grid-cols-[340px_1fr] gap-5">
            {/* Left: completed pipeline */}
            <div className="min-w-0">
              <AgentPipeline
                agents={analysis.agents}
                revisionCount={analysis.revisionCount}
              />
            </div>

            {/* Right: dashboard */}
            <div className="min-w-0">
              {/* Tab bar */}
              <div className="flex border-b border-gray-800 mb-5 bg-gray-900/40 rounded-t-2xl overflow-hidden">
                {DASH_TABS.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setDashTab(tab.id)}
                    className={`flex-1 text-xs py-3 font-ui transition-colors ${
                      dashTab === tab.id
                        ? "text-white border-b-2 border-amber-500 bg-amber-500/5"
                        : "text-gray-500 hover:text-gray-300"
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="bg-gray-900/40 border border-gray-800 rounded-b-2xl rounded-tr-2xl p-5">
                {dashTab === "budget" && <BudgetDashboard budget={budgetData} />}
                {dashTab === "investment" && (
                  <InvestmentDashboard investment={investmentData} />
                )}
                {dashTab === "stress" && (
                  <StressTestDashboard scores={stressData} />
                )}
                {dashTab === "compliance" && (
                  <ComplianceReport
                    audit={complianceData}
                    pipelineErrors={analysis.result?.pipeline_errors}
                  />
                )}
              </div>

              {/* Explainability + simulator */}
              <ExplainabilityPanel agents={analysis.agents} />
              <ScenarioSimulator onRerun={handleRerun} disabled={isRunning} />
            </div>
          </div>
        ) : (
          /* Single-column when idle or running */
          <div className="max-w-2xl mx-auto space-y-5">
            {/* Form — hidden when running (pipeline takes over) */}
            {!isRunning && (
              <FinancialProfileForm
                initialValues={loadedProfile}
                onSubmit={handleSubmit}
                disabled={isRunning}
              />
            )}

            {/* Error */}
            {analysis.error && (
              <div className="bg-red-500/8 border border-red-500/25 rounded-xl p-4">
                <p className="text-xs text-red-400 font-ui">{analysis.error}</p>
              </div>
            )}

            {/* Pipeline */}
            {showPipeline && (
              <AgentPipeline
                agents={analysis.agents}
                revisionCount={analysis.revisionCount}
              />
            )}
          </div>
        )}
      </div>
    </main>
  );
}
