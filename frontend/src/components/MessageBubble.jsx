export function MessageBubble({ message }) {
  const isUser = message.sender === "user";
  return (
    <div className={`message-row ${isUser ? "message-row-user" : "message-row-agent"}`}>
      <div className={`message-bubble ${isUser ? "message-bubble-user" : "message-bubble-agent"}`}>
        <p>{message.text}</p>
        {!isUser && message.metadata?.needsHumanHandoff ? (
          <span className="handoff-label">Human support recommended</span>
        ) : null}
      </div>
    </div>
  );
}
