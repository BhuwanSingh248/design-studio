from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import RenameClassInput


class RenameClassTool(BaseTool):
    name = "rename_class"
    description = "Rename an existing class on the design canvas."
    input_schema = RenameClassInput

    def __init__(self,
        canvas_service: CanvasService, 
        canvas_repository:CanvasRepository
    ):
        self.canvas_service = canvas_service
        self.canvas_repository = canvas_repository

    async def execute(
        self, params: RenameClassInput, context: ToolContext
    ) -> ToolResult:
        canvas = await self.canvas_repository.get(context.canvas_id)
        renamed_class = self.canvas_service.rename_class(canvas, params.class_id, params.new_name)
        await self.canvas_repository.save(context.canvas_id, canvas)
        return ToolResult(
            success=True,
            data={
                "operation": "rename_class",
                "class_id": renamed_class.id,
                "new_name": renamed_class.name,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
