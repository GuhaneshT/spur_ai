from fastapi import APIRouter, Depends,Request


router = APIRouter(prefix = "/chat", tags=["chat"])

@router.post("/message")
async def send_message():
    pass

@router.get("/{session_id}/messages")
def get_messages():
    pass