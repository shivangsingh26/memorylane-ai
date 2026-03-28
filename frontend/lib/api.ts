const BASE = "/api";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface AnalyticsData {
  message_count: Record<string, number>;
  character_count: Record<string, number>;
  message_percentage: Record<string, number>;
  top_emojis: Record<string, number>;
  top_words: Record<string, Record<string, number>>;
  response_time: {
    avg_seconds: number;
    median_seconds: number;
    min_seconds: number;
    max_seconds: number;
    sample_count: number;
  };
  initiations: Record<string, number>;
  activity_by_hour: Record<string, number[]>;
  messages_by_month: Record<string, Record<string, number>>;
  total_messages: number;
}

export interface QuizData {
  questions: {
    question: string;
    options: string[];
    answer: string;
    explanation: string;
  }[];
}

export interface TimelineData {
  phases: {
    name: string;
    period: string;
    vibe: string;
    description: string;
    key_moment: string;
  }[];
  overall_summary: string;
  fun_facts: string[];
}

export interface HealthData {
  status: string;
  model: string;
  chat_loaded: boolean;
}

// ─── Health ───────────────────────────────────────────────────────────────────

export async function fetchHealth(): Promise<HealthData> {
  const res = await fetch(`${BASE}/health`);
  if (!res.ok) throw new Error("Backend unreachable");
  return res.json();
}

// ─── Upload ───────────────────────────────────────────────────────────────────

export async function uploadChat(file: File): Promise<{ message_count: number; chunk_count: number }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/upload`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

// ─── Chat (streaming) ─────────────────────────────────────────────────────────

export async function* streamChat(
  message: string,
  user: string
): AsyncGenerator<string> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, user }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Chat failed" }));
    throw new Error(err.detail || "Chat failed");
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const payload = line.slice(6).trim();
      if (payload === "[DONE]") return;
      try {
        const parsed = JSON.parse(payload);
        if (parsed.content) yield parsed.content;
      } catch {
        // skip malformed chunk
      }
    }
  }
}

// ─── Roast ────────────────────────────────────────────────────────────────────

export async function fetchRoast(target: string): Promise<string> {
  const res = await fetch(`${BASE}/roast?target=${encodeURIComponent(target)}`);
  if (!res.ok) throw new Error("Roast failed");
  const data = await res.json();
  return data.roast as string;
}

// ─── Quiz ─────────────────────────────────────────────────────────────────────

export async function fetchQuiz(): Promise<QuizData> {
  const res = await fetch(`${BASE}/quiz`);
  if (!res.ok) throw new Error("Quiz failed");
  return res.json();
}

// ─── Timeline ─────────────────────────────────────────────────────────────────

export async function fetchTimeline(): Promise<TimelineData> {
  const res = await fetch(`${BASE}/timeline`);
  if (!res.ok) throw new Error("Timeline failed");
  return res.json();
}

// ─── Story ────────────────────────────────────────────────────────────────────

export async function fetchStory(style: string): Promise<string> {
  const res = await fetch(`${BASE}/story?style=${encodeURIComponent(style)}`);
  if (!res.ok) throw new Error("Story failed");
  const data = await res.json();
  return data.story as string;
}

// ─── Analytics ────────────────────────────────────────────────────────────────

export async function fetchAnalytics(): Promise<AnalyticsData> {
  const res = await fetch(`${BASE}/analytics`);
  if (!res.ok) throw new Error("Analytics not available");
  return res.json();
}

// ─── Delete ───────────────────────────────────────────────────────────────────

export async function deleteAllData(): Promise<void> {
  const res = await fetch(`${BASE}/data`, { method: "DELETE" });
  if (!res.ok) throw new Error("Delete failed");
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

export function formatSeconds(s: number): string {
  if (!s) return "N/A";
  if (s < 60) return `${s}s`;
  if (s < 3600) return `${Math.floor(s / 60)}m ${s % 60}s`;
  return `${Math.floor(s / 3600)}h ${Math.floor((s % 3600) / 60)}m`;
}
