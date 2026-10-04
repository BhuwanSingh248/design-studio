
from src.domain.models.canvas import CanvasState
from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
from src.tools.base import ToolContext
from src.tools.canvas.create_class import CreateClassTool
from src.tools.registry import ToolRegistry


async def main():
    repo = CanvasRepository()
    service = CanvasService()

    tool = CreateClassTool(
        canvas_service = service,
        canvas_repository = repo
    )
    
    registry = ToolRegistry()
    registry.register_tool(tool)

    canvas = CanvasState()
    await repo.save("canvas-1", canvas)

    context = ToolContext(
        workspace_id ="workspace-1",
        canvas_id="canvas-1"
    )

    result = await registry.dispatch("create_class", {"name":"Orders"}, context)
    print(f"✅ Tool Result:", result)

    saved_canvas = await repo.get("canvas-1")
    print("\ncavnas state:", saved_canvas)


import asyncio
asyncio.run(main())