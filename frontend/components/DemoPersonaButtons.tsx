"use client";

import { useState } from "react";
import { fetchDemoPersona } from "@/lib/api";

const PERSONAS = [
  {
    id: "alex" as const,
    label: "Alex",
    subtitle: "27 · Austin TX",
    detail: "$5.5k/mo · Student loans + credit card debt",
    color: "from-violet-600 to-indigo-600",
  },
  {
    id: "jordan" as const,
    label: "Jordan",
    subtitle: "42 · Chicago IL",
    detail: "$12k/mo · Mortgage + auto loan · Retirement goal",
    color: "from-emerald-600 to-teal-600",
  },
  {
    id: "sam" as const,
    label: "Sam",
    subtitle: "58 · Seattle WA",
    detail: "$18k/mo · Conservative · Retiring at 65",
    color: "from-amber-600 to-orange-600",
  },
];

interface Props {
  onLoad: (profile: Record<string, unknown>) => void;
  disabled?: boolean;
}

export default function DemoPersonaButtons({ onLoad, disabled }: Props) {
  const [loading, setLoading] = useState<string | null>(null);

  async function handleLoad(id: "alex" | "jordan" | "sam") {
    setLoading(id);
    try {
      const data = await fetchDemoPersona(id);
      onLoad(data.profile);
    } catch (err) {
      console.error("Failed to load persona:", err);
    } finally {
      setLoading(null);
    }
  }

  return (
    <div className="px-4 mb-8">
      <p className="text-center text-xs text-slate-500 uppercase tracking-widest mb-4">
        Load a demo persona
      </p>
      <div className="flex flex-col sm:flex-row gap-3 max-w-3xl mx-auto">
        {PERSONAS.map((p) => (
          <button
            key={p.id}
            onClick={() => handleLoad(p.id)}
            disabled={disabled || loading !== null}
            className={`flex-1 rounded-xl bg-gradient-to-br ${p.color} p-px disabled:opacity-40 disabled:cursor-not-allowed`}
          >
            <div className="rounded-xl bg-slate-900 hover:bg-slate-800 transition-colors px-4 py-3 text-left">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-white text-sm">
                  {p.label}
                </span>
                <span className="text-xs text-slate-400">{p.subtitle}</span>
              </div>
              <p className="text-xs text-slate-400 mt-1">{p.detail}</p>
              {loading === p.id && (
                <p className="text-xs text-indigo-400 mt-1 animate-pulse">
                  Loading...
                </p>
              )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
