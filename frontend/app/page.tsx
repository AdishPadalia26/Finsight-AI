import Link from "next/link";

const TIERS = [
  {
    icon: "◈",
    number: "01 — 03",
    label: "Data Intelligence",
    tier: "Tier 1",
    borderColor: "border-blue-500/20",
    iconColor: "text-blue-400",
    badgeColor: "bg-blue-500/10 text-blue-400",
    description:
      "Profile Builder validates and structures financial data with injection protection. Behavioral Pattern analyzes spending fingerprints and anomalies across transaction history.",
    agents: ["Profile Builder", "Behavioral Pattern", "Credit Intelligence"],
  },
  {
    icon: "⬡",
    number: "04 — 08",
    label: "Financial Planning",
    tier: "Tier 2",
    borderColor: "border-amber-500/20",
    iconColor: "text-amber-500",
    badgeColor: "bg-amber-500/10 text-amber-400",
    description:
      "Five parallel agents simultaneously design your budget framework, engineer goal timelines, optimize investments with live market data, and model tax and debt elimination strategies.",
    agents: [
      "Budget Architect",
      "Goal Engineering",
      "Investment Strategist",
      "Tax Intelligence",
      "Debt Elimination",
    ],
  },
  {
    icon: "◉",
    number: "09 — 12",
    label: "Intelligence & Safety",
    tier: "Tier 3",
    borderColor: "border-cyan-500/20",
    iconColor: "text-cyan-400",
    badgeColor: "bg-cyan-500/10 text-cyan-400",
    description:
      "Critic Agent adversarially stress-tests your plan across 5 failure scenarios — job loss, market crash, medical emergency, rate spike, inflation. Compliance Gate scans every output before delivery.",
    agents: ["Life Event", "Critic Agent", "Compliance Gate", "Memory Agent"],
  },
];

export default function Home() {
  return (
    <main className="min-h-screen bg-[#0A0F1E] relative overflow-hidden">
      {/* Amber grid background */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage: `
            linear-gradient(rgba(245,158,11,0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(245,158,11,0.025) 1px, transparent 1px)
          `,
          backgroundSize: "64px 64px",
        }}
      />

      {/* Radial glow behind hero text */}
      <div
        className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse at center, rgba(245,158,11,0.06) 0%, transparent 70%)",
        }}
      />

      {/* Hero */}
      <section className="relative z-10 flex flex-col items-center justify-center min-h-[calc(100vh-112px)] px-6 text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2.5 bg-amber-500/8 border border-amber-500/20 rounded-full px-5 py-2 mb-10">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
          <span className="text-xs font-jet text-amber-400 tracking-[0.15em]">
            12-AGENT AI PIPELINE · LANGGRAPH · HUGGINGFACE
          </span>
        </div>

        {/* Headline */}
        <h1 className="font-display text-6xl md:text-7xl lg:text-8xl text-white mb-6 leading-[1.05] max-w-5xl">
          Your bank&apos;s{" "}
          <span className="text-amber-500">AI-native</span>
          <br />
          wealth intelligence layer
        </h1>

        {/* Subtitle */}
        <p className="font-ui text-lg text-gray-400 max-w-2xl mb-4 leading-relaxed font-light">
          12 specialized AI agents. Real-time market data. Enterprise-grade
          compliance guardrails.
        </p>
        <p className="font-ui text-sm text-gray-600 max-w-xl mb-12">
          Stress-tested financial plans that adapt in real time —{" "}
          <span className="text-gray-500">
            deployable for any bank&apos;s customer base in days
          </span>
        </p>

        <div className="mb-10 grid grid-cols-3 gap-8">
          {[
            ["12", "Agents"],
            ["5", "Scenarios"],
            ["Live", "Market Data"],
          ].map(([value, label]) => (
            <div key={label} className="text-center">
              <p className="font-jet text-2xl font-bold text-amber-500">{value}</p>
              <p className="mt-1 text-xs text-gray-600 font-ui">{label}</p>
            </div>
          ))}
        </div>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row gap-3 mb-24">
          <Link
            href="/analyze"
            className="inline-flex items-center justify-center gap-2 bg-amber-500 hover:bg-amber-400 active:bg-amber-600 text-gray-950 font-semibold px-8 py-3.5 rounded-xl transition-all text-sm font-ui tracking-wide"
          >
            Start Analysis →
          </Link>
          <Link
            href="/analyze?demo=jordan"
            className="inline-flex items-center justify-center gap-2 border border-gray-700 hover:border-amber-500/40 hover:bg-amber-500/5 text-gray-300 hover:text-white px-8 py-3.5 rounded-xl transition-all text-sm font-ui"
          >
            Load Live Demo
          </Link>
        </div>

        {/* Tier cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-5xl w-full">
          {TIERS.map((tier, index) => (
            <div
              key={tier.label}
              className={`animate-fade-in bg-gray-900/50 border ${tier.borderColor} rounded-2xl p-6 text-left backdrop-blur-sm hover:bg-gray-900/80 transition-colors group`}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="flex items-start justify-between mb-4">
                <span className={`text-2xl ${tier.iconColor}`}>{tier.icon}</span>
                <span
                  className={`text-[10px] font-jet px-2 py-0.5 rounded ${tier.badgeColor}`}
                >
                  {tier.tier}
                </span>
              </div>
              <p className="font-jet text-[10px] text-gray-600 mb-1 tracking-widest">
                AGENTS {tier.number}
              </p>
              <h3 className="font-ui font-semibold text-white mb-3 text-base">
                {tier.label}
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed mb-4">
                {tier.description}
              </p>
              <div className="flex flex-wrap gap-1.5">
                {tier.agents.map((a) => (
                  <span
                    key={a}
                    className="text-[10px] font-jet text-gray-600 bg-gray-800/80 rounded px-1.5 py-0.5"
                  >
                    {a}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer strip */}
      <div className="relative z-10 border-t border-gray-800/60 py-6 text-center">
        <p className="text-xs text-gray-600 font-jet tracking-widest">
          WIPRO BFSI CLIENT VERTICAL · MULTI-AGENT ARCHITECTURE · PRODUCTION GRADE
        </p>
      </div>
    </main>
  );
}
