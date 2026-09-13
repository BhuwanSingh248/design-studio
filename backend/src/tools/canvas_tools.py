"""Concrete canvas mutation tools."""
from pydantic import BaseModel
from src.tools.base import BaseTool, ToolContext, ToolResult


class CreateClassParams(BaseModel):
    name: str
    stereotype: str = "entity"


class CreateClassTool(BaseTool):
    name = "create_class"
    description = "Add a new class or interface to the diagram canvas."
    parameters_schema = CreateClassParams

    async def execute(self, params: CreateClassParams, context: ToolContext) -> ToolResult:
        return ToolResult(success=True, data={"class_created": params.name})
