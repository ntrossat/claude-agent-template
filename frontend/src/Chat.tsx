import { ComponentProps, FormEvent, KeyboardEvent, useEffect, useRef, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { ChatEvent, loadHistory, sendMessage } from "./api";

const SESSION_KEY = "session_id";

type Message = { role: "user" | "assistant"; text: string; tools: string[] };

function describeTool(name: string, input: Record<string, unknown>): string {
  switch (name) {
    case "search":
      return `searched "${input.query}"`;
    case "read_page":
      return `read ${input.path || "the home page"}`;
    case "list_pages":
      return "listed the pages";
    case "stale_pages":
      return "checked stale pages";
    default:
      return `used ${name}`;
  }
}

// Links in replies open in a new tab, so the chat stays open.
function ExternalLink({ node, ...props }: ComponentProps<"a"> & { node?: unknown }) {
  return <a {...props} target="_blank" rel="noopener noreferrer" />;
}

function readSession(): string | null {
  try {
    return localStorage.getItem(SESSION_KEY);
  } catch {
    return null;
  }
}

function writeSession(sessionId: string | null) {
  try {
    if (sessionId) localStorage.setItem(SESSION_KEY, sessionId);
    else localStorage.removeItem(SESSION_KEY);
  } catch {
    // Storage blocked: the chat still works, it just won't survive a reload.
  }
}

export default function Chat() {
  const [sessionId, setSessionId] = useState<string | null>(readSession);
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const stored = readSession();
    if (!stored) return;
    loadHistory(stored)
      .then((history) => {
        if (history) setMessages(history.map((m) => ({ ...m, tools: [] })));
        else startNewChat();
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: "end" });
  }, [messages]);

  function startNewChat() {
    writeSession(null);
    setSessionId(null);
    setMessages([]);
    setError(null);
  }

  function updateReply(update: (reply: Message) => Message) {
    setMessages((current) => [...current.slice(0, -1), update(current[current.length - 1])]);
  }

  function handleEvent(event: ChatEvent) {
    switch (event.type) {
      case "text":
        updateReply((reply) => ({ ...reply, text: reply.text + event.delta }));
        break;
      case "tool":
        updateReply((reply) => ({ ...reply, tools: [...reply.tools, describeTool(event.name, event.input)] }));
        break;
      case "done":
        writeSession(event.session_id);
        setSessionId(event.session_id);
        break;
      case "error":
        setError(event.message);
        break;
    }
  }

  async function submit(e?: FormEvent) {
    e?.preventDefault();
    const text = draft.trim();
    if (!text || busy) return;
    setDraft("");
    setError(null);
    setBusy(true);
    setMessages((current) => [...current, { role: "user", text, tools: [] }, { role: "assistant", text: "", tools: [] }]);
    try {
      await sendMessage(text, sessionId, handleEvent);
    } catch {
      setError("The server can't be reached. Check that it is running, then send your message again.");
    } finally {
      setBusy(false);
    }
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="page">
      <header className="top-bar">
        <span className="wordmark">Agent</span>
        <button className="button secondary" type="button" onClick={startNewChat} disabled={busy || messages.length === 0}>
          New chat
        </button>
      </header>

      <main className="conversation" aria-live="polite">
        {messages.length === 0 ? (
          <div className="empty">
            <p className="status-line">new chat</p>
            <h1>Ask the agent</h1>
            <p>It answers from your team's docs and guidelines when Ohara is connected.</p>
          </div>
        ) : (
          messages.map((message, i) => (
            <article key={i} className={`message ${message.role}`}>
              {message.tools.map((tool, j) => (
                <p key={j} className="status-line">
                  {tool}
                </p>
              ))}
              {message.text ? (
                message.role === "assistant" ? (
                  <div className="markdown">
                    <Markdown remarkPlugins={[remarkGfm]} components={{ a: ExternalLink }}>
                      {message.text}
                    </Markdown>
                  </div>
                ) : (
                  <p className="message-text">{message.text}</p>
                )
              ) : (
                busy && i === messages.length - 1 && <p className="status-line">thinking…</p>
              )}
            </article>
          ))
        )}
        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}
        <div ref={endRef} />
      </main>

      <form className="composer" onSubmit={submit}>
        <label className="visually-hidden" htmlFor="message">
          Message
        </label>
        <textarea
          id="message"
          className="input"
          rows={1}
          placeholder="Ask about your docs"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onKeyDown}
          maxLength={10000}
        />
        <button className="button" type="submit" disabled={busy || !draft.trim()}>
          {busy ? "Answering…" : "Send"}
        </button>
      </form>
    </div>
  );
}
