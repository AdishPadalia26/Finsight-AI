"use client";

import { Suspense } from "react";
import AnalyzePageInner from "@/components/AnalyzePageInner";

export default function AnalyzePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#0A0F1E] flex items-center justify-center">
        <p className="text-amber-400 font-jet text-sm">Loading...</p>
      </div>
    }>
      <AnalyzePageInner />
    </Suspense>
  );
}
