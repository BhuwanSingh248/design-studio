"""Direct LLM chat endpoint."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7


class ChatResponse(BaseModel):
    reply: str
    tokens_used: int = 0


@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    return ChatResponse(
        reply=f"AI Design Studio: Received '{payload.message}'",
        tokens_used=10,
    )
