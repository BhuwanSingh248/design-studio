"""Direct LLM chat endpoint."""
from fastapi import APIRouter
from pydantic import BaseModel
from src.core.config import llm_settings
from src.llm.client import LLMClient

router = APIRouter(prefix="/chat", tags=["Chat"])

DEFAULT_TEMPERATURE = 0.7


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    tokens_used: int = 0


@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    llm_client = LLMClient(settings=llm_settings)
    response = await llm_client.chat(
        messages=[{"role": "user", "content": payload.message}],
        temperature=DEFAULT_TEMPERATURE, 
    )
    reply_text = response.choices[0].message.content if hasattr(response, "choices") else str(response)
    tokens = response.usage.total_tokens if hasattr(response, "usage") and response.usage else 0
    return ChatResponse(
        reply=reply_text,
        tokens_used=tokens,
    )
