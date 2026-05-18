const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function checkHealth(): Promise<{
  status: string;
  market_context?: Record<string, unknown>;
}> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Backend unreachable");
  return res.json();
}

export async function loadDemoPersona(persona: "alex" | "jordan" | "sam") {
  const res = await fetch(`${API_BASE}/analyze/demo/${persona}`);
  if (!res.ok) throw new Error(`Failed to load persona: ${persona}`);
  return res.json();
}
