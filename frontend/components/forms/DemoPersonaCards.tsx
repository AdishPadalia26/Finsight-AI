"use client";

import { useState } from "react";
import { User, CheckCircle, Loader2 } from "lucide-react";
import { fetchDemoPersona } from "@/lib/api";

const PERSONAS = [
  {
    id: "alex" as const,
    name: "Alex Chen",
    age: 27,
    location: "Austin, TX",
    income: "$5,500/mo",
    tagline: "Young professional · Student debt · Saving for a home",
    initial: "A",
    color: "from-violet-500/20 to-blue-500/20",
    border: "border-violet-500/30",
    activeBorder: "border-violet-400",
    dot: "bg-violet-400",
  },
  {
    id: "jordan" as const,
    name: "Jordan Kim",
    age: 42,
    location: "Chicago, IL",
    income: "$12,000/mo",
    tagline: "Mid-career · Mortgage · Retiring at 60",
    initial: "J",
    color: "from-amber-500/20 to-orange-500/20",
    border: "border-amber-500/30",
    activeBorder: "border-amber-400",
    dot: "bg-amber-400",
  },
  {
    id: "sam" as const,
    name: "Sam Rivera",
    age: 58,
    location: "Seattle, WA",
    income: "$18,000/mo",
    tagline: "Pre-retirement · Conservative · Retiring at 65",
    initial: "S",
    color: "from-cyan-500/20 to-teal-500/20",
    border: "border-cyan-500/30",
    activeBorder: "border-cyan-400",
    dot: "bg-cyan-400",
  },
];

interface Props {
  onLoad: (profile: Record<string, unknown>, id: string) => void;
  activePersona?: string | null;
  disabled?: boolean;
}

export default function DemoPersonaCards({ onLoad, activePersona, disabled }: Props) {
  const [loading, setLoading] = useState<string | null>(null);

  async function handleLoad(id: "alex" | "jordan" | "sam") {
    if (disabled || loading) return;
    setLoading(id);
    try {
      const data = await fetchDemoPersona(id);
      onLoad(data.profile ?? data, id);
    } catch {
      // silently fail — user can still fill the form manually
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="mb-6">
      <p className="text-[10px] font-jet text-gray-600 tracking-[0.2em] mb-3">
        LOAD DEMO PERSONA
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {PERSONAS.map((p) => {
          const isActive = activePersona === p.id;
          const isLoading = loading === p.id;

          return (
            <button
              key={p.id}
              onClick={() => handleLoad(p.id)}
              disabled={disabled || loading !== null}
              className={`relative text-left rounded-xl p-4 border transition-all group
                ${isActive
                  ? `${p.activeBorder} bg-gradient-to-br ${p.color}`
                  : `${p.border} hover:${p.activeBorder} bg-gray-900/50 hover:bg-gray-900/80`
                }
                disabled:opacity-40 disabled:cursor-not-allowed
              `}
            >
              <div className="flex items-start justify-between mb-3">
                <div
                  className={`w-8 h-8 rounded-full bg-gradient-to-br ${p.color} border ${p.border} flex items-center justify-center`}
                >
                  {isLoading ? (
                    <Loader2 size={14} className="animate-spin text-white" />
                  ) : isActive ? (
                    <CheckCircle size={14} className="text-white" />
                  ) : (
                    <span className="text-xs font-jet font-semibold text-white">
                      {p.initial}
                    </span>
                  )}
                </div>
                <span className="text-[10px] font-jet text-gray-600">{p.income}</span>
              </div>
              <p className="text-sm font-semibold text-white font-ui mb-0.5">
                {p.name}
              </p>
              <p className="text-[10px] text-gray-500 font-ui leading-relaxed">
                {p.tagline}
              </p>
              {isActive && (
                <div className={`absolute top-2 right-2 w-1.5 h-1.5 rounded-full ${p.dot} animate-pulse`} />
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
