from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import DeleteClassInput


class DeleteClassTool(BaseTool):
    name = "delete_class"
    description = "Delete an existing class from the design canvas by its ID."
    input_schema = DeleteClassInput

    def __init__(
        self, canvas_service: CanvasService, canvas_repository: CanvasRepository
    ):
        self.canvas_service = canvas_service
        self.canvas_repository = canvas_repository

    async def execute(
        self, params: DeleteClassInput, context: ToolContext
    ) -> ToolResult:
        canvas = await self.canvas_repository.get(context.canvas_id)
        self.canvas_service.delete_class(canvas, params.class_id)

        await self.canvas_repository.save(context.canvas_id, canvas)
        return ToolResult(
            success=True,
            data={
                "operation": "delete_class",
                "class_id": params.class_id,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
