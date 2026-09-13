"""Health and monitoring endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="", tags=["Health"])


@router.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "ai-design-studio"}


@router.get("/metrics")
async def metrics():
    return {"metrics": "prometheus format placeholder"}
