import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

export async function POST(request: NextRequest) {
  const profile = await request.json();

  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const backendResponse = await fetch(`${apiUrl}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });

  if (!backendResponse.ok || !backendResponse.body) {
    return new Response("Backend error", { status: 502 });
  }

  return new Response(backendResponse.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      "X-Accel-Buffering": "no",
    },
  });
}
