from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Message


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, conversation_id: str, sender: str, text: str, metadata: dict | None = None) -> Message:
        message = Message(
            conversation_id=conversation_id,
            sender=sender,
            text=text,
            meta=metadata or {},
        )
        self.db.add(message)
        self.db.flush()
        return message

    def list_for_conversation(self, conversation_id: str) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
        )
        return list(self.db.scalars(statement).all())

    def recent_for_conversation(self, conversation_id: str, limit: int) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(limit)
        )
        return list(reversed(self.db.scalars(statement).all()))

    def estimated_tokens_today(self, conversation_id: str) -> int:
        statement = select(Message).where(Message.conversation_id == conversation_id)
        messages = self.db.scalars(statement).all()
        return sum(int(message.meta.get("estimatedTokens", 0)) for message in messages)