from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.schemas.chat import ChatMessageResponse, HistoryResponse, MessageDto
from app.services.knowledge_service import KnowledgeService
from app.services.llm_service import LlmService
from app.services.token_budget import enforce_daily_budget, estimate_tokens


class ChatService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()
        self.conversations = ConversationRepository(db)
        self.messages = MessageRepository(db)
        self.knowledge = KnowledgeService(db)
        self.llm = LlmService()

    async def send_message(self, text: str, session_id: str | None) -> ChatMessageResponse:
        conversation = self.conversations.get_or_create(session_id, channel="live_chat")

        try:
            enforce_daily_budget(self.messages.estimated_tokens_today(conversation.id), text)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc)) from exc

        self.messages.create(
            conversation_id=conversation.id,
            sender="user",
            text=text,
            metadata={"estimatedTokens": estimate_tokens(text)},
        )
        self.db.commit()

        history = self.messages.recent_for_conversation(conversation.id, self.settings.history_limit)
        relevant_knowledge = self.knowledge.relevant_items(text)
        result = await self.llm.generate(text, relevant_knowledge, history)

        if result.metadata.get("needsHumanHandoff"):
            self.conversations.mark_handoff_needed(conversation)

        self.messages.create(
            conversation_id=conversation.id,
            sender="ai",
            text=result.reply,
            metadata={
                **result.metadata,
                "knowledgeTitles": [item.title for item in relevant_knowledge],
            },
        )
        self.db.commit()
        return ChatMessageResponse(reply=result.reply, sessionId=conversation.id, metadata=result.metadata)

    def history(self, session_id: str) -> HistoryResponse:
        conversation = self.conversations.get(session_id)
        if not conversation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found.")

        messages = [
            MessageDto(
                id=message.id,
                sender=message.sender,
                text=message.text,
                metadata=message.meta,
                createdAt=message.created_at,
            )
            for message in self.messages.list_for_conversation(session_id)
        ]
        return HistoryResponse(sessionId=session_id, messages=messages)
