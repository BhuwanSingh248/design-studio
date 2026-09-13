"""FastAPI dependencies."""
from typing import Generator
from fastapi import Header, HTTPException, status


async def get_workspace_id(x_workspace_id: str = Header(...)) -> str:
    if not x_workspace_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Workspace-Id header required",
        )
    return x_workspace_id
