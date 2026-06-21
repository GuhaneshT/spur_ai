import { useEffect, useMemo, useRef, useState } from "react";
import { RotateCcw, Send } from "lucide-react";
import { loadMessages, sendChatMessage } from "../api/chatApi.js";
import { MessageBubble } from "./MessageBubble.jsx";
import { TypingIndicator } from "./TypingIndicator.jsx";

const SESSION_STORAGE_KEY = "spur.liveChat.sessionId";
const STARTER_CHIPS = [
  "What is your return policy?",
  "Do you ship to the USA?",
  "How long does delivery take?",
  "What are support hours?",
];

export function ChatWidget() {
  const [sessionId, setSessionId] = useState(() => localStorage.getItem(SESSION_STORAGE_KEY));
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const listRef = useRef(null);

  const canSend = useMemo(() => draft.trim().length > 0 && !isLoading, [draft, isLoading]);

  useEffect(() => {
    if (!sessionId) return;
    let cancelled = false;

    loadMessages(sessionId)
      .then((data) => {
        if (!cancelled) setMessages(data.messages);
      })
      .catch(() => {
        localStorage.removeItem(SESSION_STORAGE_KEY);
        if (!cancelled) setSessionId(null);
      });

    return () => {
      cancelled = true;
    };
  }, [sessionId]);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading]);

  async function handleSend(text = draft) {
    const trimmed = text.trim();
    if (!trimmed || isLoading) return;

    const optimisticMessage = {
      id: `local-${Date.now()}`,
      sender: "user",
      text: trimmed,
      metadata: {},
      createdAt: new Date().toISOString(),
    };

    setDraft("");
    setError("");
    setIsLoading(true);
    setMessages((current) => [...current, optimisticMessage]);

    try {
      const data = await sendChatMessage({ message: trimmed, sessionId });
      if (!sessionId) {
        localStorage.setItem(SESSION_STORAGE_KEY, data.sessionId);
        setSessionId(data.sessionId);
      }
      setMessages((current) => [
        ...current,
        {
          id: `ai-${Date.now()}`,
          sender: "ai",
          text: data.reply,
          metadata: data.metadata || {},
          createdAt: new Date().toISOString(),
        },
      ]);
    } catch (err) {
      setError(err.message);
      setMessages((current) => current.filter((message) => message.id !== optimisticMessage.id));
    } finally {
      setIsLoading(false);
    }
  }

  function resetSession() {
    localStorage.removeItem(SESSION_STORAGE_KEY);
    setSessionId(null);
    setMessages([]);
    setError("");
    setDraft("");
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }

  return (
    <main className="app-shell">
      <section className="chat-surface" aria-label="Northstar Outfitters live chat">
        <header className="chat-header">
          <div>
            <p className="eyebrow">Northstar Outfitters</p>
            <h1>Live Support</h1>
          </div>
          <button className="icon-button" type="button" onClick={resetSession} aria-label="Reset conversation">
            <RotateCcw size={18} />
          </button>
        </header>

        <div className="starter-strip" aria-label="Starter questions">
          {STARTER_CHIPS.map((chip) => (
            <button key={chip} type="button" onClick={() => handleSend(chip)} disabled={isLoading}>
              {chip}
            </button>
          ))}
        </div>

        <div className="message-list" ref={listRef} aria-live="polite">
          {messages.length === 0 ? (
            <div className="empty-state">
              <p>Ask about shipping, delivery, returns, warranty, payments, cancellations, or support hours.</p>
            </div>
          ) : (
            messages.map((message) => <MessageBubble key={message.id} message={message} />)
          )}
          {isLoading ? <TypingIndicator /> : null}
        </div>

        {error ? <p className="error-banner">{error}</p> : null}

        <form
          className="composer"
          onSubmit={(event) => {
            event.preventDefault();
            handleSend();
          }}
        >
          <textarea
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message"
            rows={1}
            maxLength={2000}
            disabled={isLoading}
          />
          <button className="send-button" type="submit" disabled={!canSend} aria-label="Send message">
            <Send size={18} />
          </button>
        </form>
      </section>
    </main>
  );
}
