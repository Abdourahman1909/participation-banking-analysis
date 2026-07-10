import type {
  CampaignList,
  ChatResponse,
  PipelineStatus,
  RunEvent,
  RunInfo,
  Stats,
  Step,
} from "./types";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`${path}: ${res.status}`);
  return res.json();
}

export const fetchStats = () => get<Stats>("/api/stats");
export const fetchCampaigns = () => get<CampaignList>("/api/campaigns");
export const fetchPipelineStatus = () => get<PipelineStatus>("/api/pipeline/status");
export const fetchRuns = () => get<RunInfo[]>("/api/pipeline/runs");

export async function sendChat(question: string): Promise<ChatResponse> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!res.ok) throw new Error(`chat: ${res.status}`);
  return res.json();
}

export async function startRun(step: Step): Promise<{ run_id: number }> {
  const res = await fetch("/api/pipeline/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ step }),
  });
  if (res.status === 409) throw new Error("busy");
  if (!res.ok) throw new Error(`run: ${res.status}`);
  return res.json();
}

/**
 * Subscribe to a run's SSE stream (ADR 0022). Replays stored events, then
 * tails live ones; the server sends `event: end` when the run is finished.
 * Returns the close function.
 */
export function subscribeRunEvents(
  runId: number,
  onEvent: (e: RunEvent) => void,
  onEnd: () => void,
): () => void {
  const es = new EventSource(`/api/pipeline/runs/${runId}/events`);
  es.onmessage = (msg) => {
    try {
      onEvent(JSON.parse(msg.data) as RunEvent);
    } catch {
      /* malformed frame — skip */
    }
  };
  es.addEventListener("end", () => {
    es.close();
    onEnd();
  });
  es.onerror = () => {
    /* EventSource auto-reconnects; a closed run ends via `end` above. */
  };
  return () => es.close();
}
