"""LangGraph agent execution and approval resume endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/agent", tags=["Agent"])


class ResumeRequest(BaseModel):
    thread_id: str
    approved: bool
    feedback: str | None = None


@router.post("/resume")
async def resume_agent(payload: ResumeRequest):
    return {"status": "resumed", "approved": payload.approved}
