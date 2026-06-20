from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import get_settings


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)
    sessionId: str | None = None

    @property
    def session_id(self) -> str | None:
        return self.sessionId

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        stripped = value.strip()
        settings = get_settings()
        if not stripped:
            raise ValueError("Message cannot be empty.")
        if len(stripped) > settings.max_input_chars:
            raise ValueError(f"Message cannot exceed {settings.max_input_chars} characters.")
        return stripped


class ChatMessageResponse(BaseModel):
    reply: str
    sessionId: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MessageDto(BaseModel):
    id: int
    sender: str
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class HistoryResponse(BaseModel):
    sessionId: str
    messages: list[MessageDto]