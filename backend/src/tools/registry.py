"""Tool registry for declaring and dispatching LLM tools."""
from src.tools.base import BaseTool, ToolContext, ToolResult


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    async def dispatch(self, name: str, params: dict, context: ToolContext) -> ToolResult:
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(success=False, error=f"Unknown tool: {name}")
        try:
            validated_params = tool.parameters_schema(**params)
            return await tool.execute(validated_params, context)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
