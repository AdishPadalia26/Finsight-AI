"use client";

import { useState, useCallback, useRef } from "react";
import { streamAnalysis } from "@/lib/api";
import type {
  AnalyzeRequest,
  AgentState,
  SSEEvent,
  AnalysisStatus,
} from "@/lib/types";

export interface AnalysisState {
  agents: Record<string, AgentState>;
  result: SSEEvent | null;
  status: AnalysisStatus;
  error: string | null;
  revisionCount: number;
}

export function useAnalysis() {
  const [agents, setAgents] = useState<Record<string, AgentState>>({});
  const [result, setResult] = useState<SSEEvent | null>(null);
  const [status, setStatus] = useState<AnalysisStatus>("idle");
  const [error, setError] = useState<string | null>(null);
  const [revisionCount, setRevisionCount] = useState(0);
  const cancelRef = useRef<(() => void) | null>(null);

  const run = useCallback((body: AnalyzeRequest) => {
    cancelRef.current?.();
    setAgents({});
    setResult(null);
    setError(null);
    setRevisionCount(0);
    setStatus("running");

    cancelRef.current = streamAnalysis(
      body,
      (e: SSEEvent) => {
        switch (e.event) {
          case "agent_start":
            if (e.agent && e.label) {
              setAgents((prev) => ({
                ...prev,
                [e.agent!]: { label: e.label!, status: "running" },
              }));
            }
            break;

          case "agent_complete":
            if (e.agent) {
              setAgents((prev) => ({
                ...prev,
                [e.agent!]: {
                  label: prev[e.agent!]?.label ?? e.label ?? e.agent!,
                  status: "complete",
                  summary: e.summary,
                },
              }));
            }
            break;

          case "revision_loop":
            setRevisionCount(e.revision_number ?? 0);
            // reset Tier 2 agents to re-running
            setAgents((prev) => {
              const tier2 = [
                "budget_architect",
                "goal_engineering",
                "investment_strategist",
                "tax_intelligence",
                "debt_elimination",
                "life_event",
              ];
              const next = { ...prev };
              for (const key of tier2) {
                if (next[key]) next[key] = { ...next[key], status: "running" };
              }
              return next;
            });
            break;

          case "pipeline_complete":
            setResult(e);
            setStatus("complete");
            break;

          case "pipeline_error":
            setError(e.message ?? "Unknown error");
            setStatus("error");
            break;
        }
      },
      (err) => {
        setError(err);
        setStatus("error");
      }
    );
  }, []);

  const cancel = useCallback(() => {
    cancelRef.current?.();
    setStatus("idle");
  }, []);

  return { agents, result, status, error, revisionCount, run, cancel };
}
