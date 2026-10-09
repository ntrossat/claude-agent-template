// All server calls. Every URL is built from the base path the server puts in the page.

const meta = document.querySelector<HTMLMetaElement>('meta[name="base-path"]')?.content ?? "";
const BASE_PATH = meta.startsWith("%") ? "" : meta;

export type ChatEvent =
  | { type: "text"; delta: string }
  | { type: "tool"; name: string; input: Record<string, unknown> }
  | { type: "done"; session_id: string }
  | { type: "error"; message: string };

export type HistoryMessage = { role: "user" | "assistant"; text: string };

export class ApiError extends Error {}

async function errorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") return body.detail;
  } catch {
    // Not JSON: fall through to the generic message.
  }
  return `The server answered ${response.status}. Reload the page and try again.`;
}

export async function loadHistory(sessionId: string): Promise<HistoryMessage[] | null> {
  const response = await fetch(`${BASE_PATH}/api/chat/${sessionId}`);
  if (response.status === 404 || response.status === 422) return null;
  if (!response.ok) throw new ApiError(await errorMessage(response));
  return response.json();
}

export async function sendMessage(message: string, sessionId: string | null, onEvent: (event: ChatEvent) => void): Promise<void> {
  const response = await fetch(`${BASE_PATH}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  if (!response.ok || !response.body) throw new ApiError(await errorMessage(response));

  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += value;
    const frames = buffer.split("\n\n");
    buffer = frames.pop() ?? "";
    for (const frame of frames) {
      if (frame.startsWith("data: ")) onEvent(JSON.parse(frame.slice(6)) as ChatEvent);
    }
  }
}
