"""API v1 routes."""
from fastapi import APIRouter
from src.api.v1.chat import router as chat_router
from src.api.v1.canvas import router as canvas_router
from src.api.v1.agent import router as agent_router
from src.api.v1.ws import router as ws_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(chat_router)
api_v1_router.include_router(canvas_router)
api_v1_router.include_router(agent_router)
api_v1_router.include_router(ws_router)

__all__ = ["api_v1_router"]
