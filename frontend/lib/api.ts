import type { AnalyzeRequest, SSEEvent } from "./types";

// With static export (S3 + CloudFront), there is no Next.js server.
// All calls go directly to the FastAPI backend (ALB URL).
const API_BASE =
  (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

// Embedded fallback profiles — used when the backend /analyze/demo/* endpoint
// is unreachable (e.g. network timeout during demo setup).
const DEMO_PROFILES: Record<string, Record<string, unknown>> = {
  alex: {
    age: 27,
    location: "Austin, TX",
    employment_status: "full_time",
    monthly_income: 5500,
    monthly_expenses: 4200,
    savings: 8000,
    investments: 3000,
    property_value: 0,
    debts: [
      { type: "student_loan", balance: 28000, interest_rate: 5.5, minimum_payment: 290 },
      { type: "credit_card", balance: 3200, interest_rate: 22.9, minimum_payment: 85 },
    ],
    goals: [
      { description: "Emergency fund (3 months expenses)", target_amount: 16500, timeline_months: 18, priority: "critical" },
      { description: "Buy a home (20% down payment)", target_amount: 60000, timeline_months: 48, priority: "high" },
    ],
    risk_tolerance: "moderate",
    investment_horizon: 35,
    tax_bracket: 0.22,
    recent_life_events: ["new_job"],
  },
  jordan: {
    age: 29,
    location: "San Francisco, CA",
    employment_status: "full_time",
    monthly_income: 9500,
    monthly_expenses: 6200,
    savings: 18000,
    investments: 12000,
    property_value: 0,
    debts: [
      { type: "student_loan", balance: 34000, interest_rate: 5.5, minimum_payment: 380 },
    ],
    goals: [
      { description: "Emergency fund", target_amount: 28500, timeline_months: 12, priority: "high" },
      { description: "Down payment", target_amount: 120000, timeline_months: 60, priority: "medium" },
    ],
    risk_tolerance: "moderate",
    investment_horizon: 15,
    tax_bracket: 0.22,
    recent_life_events: [],
  },
  sam: {
    age: 58,
    location: "Seattle, WA",
    employment_status: "full_time",
    monthly_income: 18000,
    monthly_expenses: 9000,
    savings: 120000,
    investments: 680000,
    property_value: 750000,
    debts: [
      { type: "mortgage", balance: 85000, interest_rate: 2.9, minimum_payment: 720 },
    ],
    goals: [
      { description: "Retire at 65", target_amount: 2500000, timeline_months: 84, priority: "critical" },
      { description: "Travel fund", target_amount: 80000, timeline_months: 84, priority: "medium" },
    ],
    risk_tolerance: "conservative",
    investment_horizon: 7,
    tax_bracket: 0.24,
    recent_life_events: [],
  },
};

export async function fetchDemoPersona(
  persona: "alex" | "jordan" | "sam"
): Promise<{ persona: string; profile: Record<string, unknown> }> {
  try {
    const res = await fetch(`${API_BASE}/analyze/demo/${persona}`, {
      signal: AbortSignal.timeout(4000),
    });
    if (res.ok) return res.json();
  } catch {
    // Network error or timeout — fall through to embedded data
  }
  return { persona, profile: DEMO_PROFILES[persona] };
}

export function streamAnalysis(
  body: AnalyzeRequest,
  onEvent: (e: SSEEvent) => void,
  onError: (err: string) => void
): () => void {
  const controller = new AbortController();

  fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok || !res.body) {
        onError(`HTTP ${res.status}`);
        return;
      }
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() ?? "";
        for (const chunk of chunks) {
          const dataLine = chunk
            .split("\n")
            .find((l) => l.startsWith("data: "));
          if (dataLine) {
            try {
              onEvent(JSON.parse(dataLine.slice(6)) as SSEEvent);
            } catch {
              // skip malformed SSE frame
            }
          }
        }
      }
    })
    .catch((err) => {
      if ((err as Error).name !== "AbortError") {
        onError(String(err));
      }
    });

  return () => controller.abort();
}
