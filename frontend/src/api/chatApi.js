const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8001";

async function parseResponse(response) {
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(body.detail)
      ? body.detail.map((error) => error.msg).join(" ")
      : body.detail || "Request failed. Please try again.";
    throw new Error(detail);
  }
  return body;
}

export async function sendChatMessage({ message, sessionId }) {
  const response = await fetch(`${API_BASE_URL}/chat/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, sessionId }),
  });
  return parseResponse(response);
}

export async function loadMessages(sessionId) {
  const response = await fetch(`${API_BASE_URL}/chat/${sessionId}/messages`);
  return parseResponse(response);
}
