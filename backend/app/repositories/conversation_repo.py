from sqlalchemy.orm import Session

from app.models import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, conversation_id: str) -> Conversation | None:
        return self.db.get(Conversation, conversation_id)

    def get_or_create(self, conversation_id: str | None, channel: str = "live_chat") -> Conversation:
        if conversation_id:
            existing = self.get(conversation_id)
            if existing:
                return existing

        conversation = Conversation(channel=channel)
        self.db.add(conversation)
        self.db.flush()
        return conversation

    def mark_handoff_needed(self, conversation: Conversation) -> None:
        conversation.status = "handoff_requested"
        self.db.add(conversation)