"""Small manual smoke test for registered canvas tools."""

import asyncio

from src.domain.models.canvas import CanvasState
from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
from src.tools.base import ToolContext
from src.tools.canvas.create_class import CreateClassTool
from src.tools.registry import ToolRegistry


async def main():
    workspace_id = "workspace-1"
    canvas_id = "canvas-1"
    repository = CanvasRepository()
    service = CanvasService()

    await repository.save(workspace_id, canvas_id, CanvasState())
    registry = ToolRegistry()
    registry.register_tool(
        CreateClassTool(canvas_service=service, canvas_repository=repository)
    )

    context = ToolContext(workspace_id=workspace_id, canvas_id=canvas_id)
    result = await registry.dispatch("create_class", {"name": "Orders"}, context)
    saved_canvas = await repository.get(workspace_id, canvas_id)

    print("Tool result:", result)
    print("Canvas state:", saved_canvas)


if __name__ == "__main__":
    asyncio.run(main())
