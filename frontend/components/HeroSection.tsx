"use client";

export default function HeroSection() {
  return (
    <header className="text-center py-14 px-4">
      <div className="inline-flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-full px-4 py-1.5 text-xs text-slate-400 mb-6">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        12-agent AI pipeline · LangGraph · HuggingFace
      </div>

      <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-4">
        FinSight AI
      </h1>

      <p className="text-lg text-slate-400 max-w-2xl mx-auto mb-2">
        Your bank&apos;s AI-native wealth intelligence layer.
      </p>

      <p className="text-sm text-slate-500 max-w-xl mx-auto">
        Multi-agent financial analysis with Critic stress-testing, Compliance
        guardrails, and real-time market data — built for the Wipro FDE
        Pre-screening Assignment.
      </p>
    </header>
  );
}
