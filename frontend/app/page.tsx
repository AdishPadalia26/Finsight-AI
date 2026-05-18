"use client";

import { useState } from "react";
import HeroSection from "@/components/HeroSection";
import DemoPersonaButtons from "@/components/DemoPersonaButtons";
import ProfileForm from "@/components/ProfileForm";
import PipelineView from "@/components/PipelineView";
import ResultsDashboard from "@/components/ResultsDashboard";
import ExplainabilityPanel from "@/components/ExplainabilityPanel";
import ScenarioSimulator from "@/components/ScenarioSimulator";
import { useAnalysis } from "@/hooks/useAnalysis";
import type { FinancialProfile } from "@/lib/types";

export default function Home() {
  const analysis = useAnalysis();
  const [loadedProfile, setLoadedProfile] = useState<Record<string, unknown> | null>(null);

  function handleSubmit(profile: FinancialProfile) {
    const p = profile as unknown as Record<string, unknown>;
    const body = p.raw_input
      ? { raw_input: p.raw_input as string }
      : { profile: p };
    analysis.run(body);
  }

  function handleRerun(overrides: Record<string, number>) {
    if (!loadedProfile) return;
    analysis.run({
      profile: { ...loadedProfile, scenario_overrides: overrides },
    });
  }

  const isRunning  = analysis.status === "running";
  const showPipeline = analysis.status !== "idle";
  const showResults  = analysis.status === "complete" && analysis.result !== null;

  return (
    <main className="min-h-screen bg-slate-950">
      <HeroSection />

      <DemoPersonaButtons
        onLoad={(profile) => setLoadedProfile(profile)}
        disabled={isRunning}
      />

      <ProfileForm
        initialValues={loadedProfile}
        onSubmit={handleSubmit}
        disabled={isRunning}
      />

      {analysis.error && (
        <div className="max-w-3xl mx-auto px-4 mb-6">
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4">
            <p className="text-sm text-red-400">{analysis.error}</p>
          </div>
        </div>
      )}

      {showPipeline && (
        <PipelineView
          agents={analysis.agents}
          revisionCount={analysis.revisionCount}
        />
      )}

      {showResults && analysis.result && (
        <>
          <ResultsDashboard data={analysis.result} />
          <ExplainabilityPanel agents={analysis.agents} />
          <ScenarioSimulator onRerun={handleRerun} disabled={isRunning} />
        </>
      )}
    </main>
  );
}
