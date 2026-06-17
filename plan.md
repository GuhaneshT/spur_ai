# AI Live Chat Agent - Build Plan

Spur Founding Full-Stack Engineer Take-Home | FastAPI backend + React frontend

## Main Strategy

Ship a polished, boring, reliable MVP. The app should work end-to-end, persist conversations, control token cost, fail gracefully, and be structured so future channels like WhatsApp, Instagram, and live chat can share the same conversation engine.

## 1. Stack

| Area | Choice |
| --- | --- |
| Frontend | React + Vite. |
| Backend | Python + FastAPI |
| Persistence | SQLLite. |
| LLM | OpenAI. |
| Cost control | Message length limits, history caps, relevant FAQ selection, rate limiting. |

## 2. Architecture

React UI -> FastAPI route -> Chat service -> Repositories + LLM service -> Database + LLM provider


## 4. API Contract

| Endpoint | Purpose | Response |
| --- | --- | --- |
| `POST /chat/message` | Send message and generate reply. | `{ reply, sessionId }` |
| `GET /chat/{sessionId}/messages` | Load previous messages on reload. | `{ sessionId, messages[] }` |
| `GET /health` | Deployment health check. | `{ status: "ok" }` |

## 5. Data Model

| Table | Fields |
| --- | --- |
| `conversations` | `id`, `channel`, `status`, `created_at`, `updated_at` 
| `messages` | `id`, `conversation_id`, `sender`, `text`, `metadata`, `created_at` 
| `knowledge_items` | `id`, `title`, `category`, `content`, `enabled` 

## 6. LLM and FAQ Strategy

Seed a fictional store
Outfitters, with shipping, returns, support hours, warranty, cancellation, and payment FAQs.

Use a strict support prompt: answer only from provided knowledge, stay concise, do not invent policies, and escalate when unsure.

Use recent history for context, but cap it to control tokens.

Prompt rules: answer only from store knowledge; do not invent policies or timelines; if unsure, suggest human support; keep replies under 120 words; ask one clarifying question if needed.

## 7. Token and Cost Controls

| Control | Rule | Reason |
| --- | --- | --- |
| Input cap | Reject or warn above 2,000 chars. | Prevents prompt bloat and abuse. |
| History cap | Send last 10-12 messages only. | Keeps context useful but bounded. |
| FAQ selection | Keyword-match relevant FAQ items first. | Cheaper than sending all knowledge. |
| Output cap | 250-350 max output tokens. | Predictable cost and concise replies. |
| Timeout | 10-15 seconds. | Avoids hanging requests. |

## 8. Rate Limiting

| Limit | Suggested Rule | Implementation |
| --- | --- | --- |
| Per IP | 20 messages/min | In-memory locally; Redis in production. |
| Per session | 10 messages/min | Blocks runaway sessions. |
| Concurrency | 1 in-flight request/session | Prevents duplicate sends and cost spikes. |
| Daily budget | Optional 20k estimated tokens/session/day | Good README discussion even if simple. |

## 9. Security and Robustness

| Area | Requirement |
| --- | --- |
| Secrets | Use `.env` and `.env.example`. Never commit API keys. |
| Validation | Pydantic schemas; reject empty, whitespace-only, and oversized messages. |
| CORS | Allowlist frontend origin in deployed app. |
| Session IDs | Use UUIDs, not sequential IDs. |
| Errors | Catch LLM, DB, timeout, and rate-limit failures. Never expose stack traces to frontend. |
| Logging | Log request ID, latency, and error type. Avoid full customer-message logs in production. |

## 10. Frontend UX

Scrollable message list with distinct user and AI bubbles.

Input, send button, Enter-to-send, disabled send while loading.

Agent is typing indicator and auto-scroll to latest message.

Persist `sessionId` in `localStorage` and load history on page load.

Starter chips: return policy, shipping to USA, delivery time, support hours.

## 11. Human Handoff Simulation

When the answer is unknown, order-specific, or sensitive, the assistant should recommend human support and store handoff metadata.

```json
{
  "metadata": {
    "needsHumanHandoff": true,
    "reason": "unknown_policy"
  },
  "reply": "I may need a teammate to help with this specific issue. Please contact support at support@northstar.example."
}
```

## 12. Testing Plan

| Area | Tests | Why |
| --- | --- | --- |
| Validation | Empty, whitespace-only, oversized messages | Proves robustness. |
| Sessions | New session creation, existing session reuse | Proves persistence flow. |
| Messages | User and AI messages are stored in order | Proves reload/history requirement. |
| LLM failures | Mock timeout/error and return fallback | Proves backend never crashes. |
| Rate limiting | Abusive traffic is blocked cleanly | Proves cost protection. |
