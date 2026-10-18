from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import RemoveMethodInput


class RemoveMethodTool(BaseTool):
    name = "remove_method"
    description = "Remove a method from a class on the canvas."
    input_schema = RemoveMethodInput

    def __init__(
        self,
        canvas_service: CanvasService,
        canvas_repository: CanvasRepository,
    ):
        self.canvas_service = canvas_service
        self.canvas_repository = canvas_repository

    async def execute(
        self, params: RemoveMethodInput, context: ToolContext
    ) -> ToolResult:
        canvas = await self.canvas_repository.get(
            context.workspace_id, context.canvas_id
        )
        method = self.canvas_service.remove_method(
            canvas, params.class_id, params.name
        )
        await self.canvas_repository.save(
            context.workspace_id, context.canvas_id, canvas
        )
        return ToolResult(
            success=True,
            data={
                "operation": "remove_method",
                "class_id": params.class_id,
                "method_name": method.name,
                "return_type": method.return_type,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
