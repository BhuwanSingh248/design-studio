"""Direct LLM chat endpoint."""
from fastapi import APIRouter
from pydantic import BaseModel
from src.core.config import llm_settings
from src.llm.client import LLMClient
from src.llm.schemas import DesignReview

router = APIRouter(prefix="/chat", tags=["Chat"])

DEFAULT_TEMPERATURE = 0.7


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply:DesignReview


@router.post("", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    llm_client = LLMClient(settings=llm_settings)
    response = await llm_client.chat_structured(payload.message, DesignReview)
    return ChatResponse(
        reply=response,
    )
