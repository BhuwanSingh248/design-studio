from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import RenameClassInput


class RenameClassTool(BaseTool):
    name = "rename_class"
    description = "Rename an existing class on the design canvas."
    input_schema = RenameClassInput

    def __init__(self,canvas_service: CanvasService, canvas_repository:CanvasRepository):
        self.canvas_service = canvas_service
        self.canvas_repository = canvas_repository

    async def execute(
        self, params: RenameClassInput, context: ToolContext
    ) -> ToolResult:
        canvas = await self.canvas_repository.get_canvas(context.workspace_id, context.canvas_id)
        self.canvas_service.rename_class(canvas, params.class_id, params.new_name)
        await self.canvas_repository.save(context.workspace_id, context.canvas_id, canvas)
        return ToolResult(
            success=True,
            data={
                "operation": "renamed_class",
                "class_id": params.class_id,
                "new_name": params.new_name,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
