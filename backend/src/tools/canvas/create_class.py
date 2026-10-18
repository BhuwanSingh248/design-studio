from src.domain.repositories.canvas_repository import CanvasRepository
from src.domain.services.canvas_service import CanvasService
from src.tools.base import BaseTool, ToolContext, ToolResult
from src.tools.schemas import CreateClassInput


class CreateClassTool(BaseTool):
    name = "create_class"
    description = "Create a new class on the design canvas."
    input_schema = CreateClassInput

    def __init__(
        self,
        canvas_service: CanvasService,
        canvas_repository: CanvasRepository,
    ):
        self.canvas_service = canvas_service
        self.canvas_repository = canvas_repository

    async def execute(
        self, params: CreateClassInput, context: ToolContext
    ) -> ToolResult:
        canvas = await self.canvas_repository.get(
            context.workspace_id, context.canvas_id
        )
        created_class = self.canvas_service.create_class(canvas, params.name)
        await self.canvas_repository.save(
            context.workspace_id, context.canvas_id, canvas
        )
        return ToolResult(
            success=True,
            data={
                "operation": "create_class",
                "class_name": created_class.name,
                "class_id": created_class.id,
                "workspace_id": context.workspace_id,
                "canvas_id": context.canvas_id,
            },
        )
