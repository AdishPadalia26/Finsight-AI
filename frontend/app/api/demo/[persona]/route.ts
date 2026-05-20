import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

const FALLBACK_PROFILES: Record<string, Record<string, unknown>> = {
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
      { type: "student_loan",  balance: 28000, interest_rate: 5.5,  minimum_payment: 290 },
      { type: "credit_card",   balance: 3200,  interest_rate: 22.9, minimum_payment: 85  },
    ],
    goals: [
      { description: "Emergency fund (3 months expenses)", target_amount: 16500,  timeline_months: 18, priority: "critical" },
      { description: "Buy a home (20% down payment)",      target_amount: 60000,  timeline_months: 48, priority: "high" },
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
      { description: "Emergency fund", target_amount: 28500, timeline_months: 12, priority: "high"   },
      { description: "Down payment",   target_amount: 120000, timeline_months: 60, priority: "medium" },
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
      { description: "Retire at 65",  target_amount: 2500000, timeline_months: 84, priority: "critical" },
      { description: "Travel fund",   target_amount: 80000,   timeline_months: 84, priority: "medium"   },
    ],
    risk_tolerance: "conservative",
    investment_horizon: 7,
    tax_bracket: 0.24,
    recent_life_events: [],
  },
};

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ persona: string }> }
) {
  const { persona } = await params;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  // Try the backend first (has full profile including agent result fields)
  try {
    const backendResponse = await fetch(`${apiUrl}/analyze/demo/${persona}`, {
      signal: AbortSignal.timeout(4000),
    });
    if (backendResponse.ok) {
      return new Response(backendResponse.body, {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });
    }
  } catch {
    // Fall through to local fallback
  }

  // Local fallback — covers all three personas
  const profile = FALLBACK_PROFILES[persona];
  if (!profile) {
    return Response.json({ error: `Persona '${persona}' not found.` }, { status: 404 });
  }

  return Response.json({ persona, profile });
}
