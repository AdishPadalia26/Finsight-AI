import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  const body = await request.json();
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  try {
    const backendResponse = await fetch(`${apiUrl}/scenario`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (backendResponse.ok) {
      return new Response(backendResponse.body, {
        status: 200,
        headers: { "Content-Type": backendResponse.headers.get("Content-Type") ?? "application/json" },
      });
    }
  } catch {
    // Fall through to deterministic local demo response.
  }

  const modifier = (body.scenario ?? body.modifier ?? {}) as Record<string, number | string>;
  const profile = (body.profile ?? {}) as Record<string, number>;
  const income = Number(profile.monthly_income ?? 0);
  const expenses = Number(profile.monthly_expenses ?? 0);
  const savings = Number(profile.savings ?? 0);
  const baseScore = income > 0 ? Math.max(0, Math.min(100, ((income - expenses) / income) * 100 + Math.min(savings / Math.max(expenses, 1), 6) * 8)) : 0;
  const penalty = Number(modifier.penalty ?? 12);
  const newScore = Math.max(0, Math.round(baseScore - penalty));

  return Response.json({
    status: "simulated",
    health_score: newScore,
    delta: Math.round(newScore - baseScore),
  });
}
