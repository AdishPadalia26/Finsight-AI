import type { AnalyzeRequest, SSEEvent } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function fetchDemoPersona(
  persona: "alex" | "jordan" | "sam"
): Promise<{ persona: string; profile: Record<string, unknown> }> {
  const res = await fetch(`${API_BASE}/analyze/demo/${persona}`);
  if (!res.ok) throw new Error(`Failed to load persona: ${persona}`);
  return res.json();
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
