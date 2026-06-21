from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse, HistoryResponse
from app.services.chat_service import ChatService
from app.services.rate_limiter import enforce_chat_rate_limit


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
async def send_message(payload: ChatMessageRequest, request: Request, db: Session = Depends(get_db)) -> ChatMessageResponse:
    client_host = request.client.host if request.client else "unknown"
    enforce_chat_rate_limit(client_host, payload.session_id)
    return await ChatService(db).send_message(payload.message, payload.session_id)


@router.get("/{session_id}/messages", response_model=HistoryResponse)
def get_messages(session_id: str, db: Session = Depends(get_db)) -> HistoryResponse:
    return ChatService(db).history(session_id)
