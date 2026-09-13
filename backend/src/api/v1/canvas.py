"""Canvas state manipulation and query endpoints."""
from fastapi import APIRouter

router = APIRouter(prefix="/canvas", tags=["Canvas"])


@router.get("/{canvas_id}")
async def get_canvas(canvas_id: str):
    return {"canvas_id": canvas_id, "nodes": [], "edges": []}
