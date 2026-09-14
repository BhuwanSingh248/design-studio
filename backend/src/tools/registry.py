"""Tool registry for declaring and dispatching LLM tools."""
from src.tools.base import BaseTool, ToolContext, ToolResult


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register_tool(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool {tool.name} already registered")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    @property
    def schemas(self):
        schema_list = {"tools": []}
        for tool_name, tool in self._tools.items():
            schema_list["tools"].append(
                {
                    "name": tool_name,
                    "description": tool.description,
                    "input_schema": tool.input_schema.model_json_schema(),
                }
            )
        return schema_list
        
    async def dispatch(self, name: str, params: dict, context: ToolContext) -> ToolResult:
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(success=False, error=f"Unknown tool: {name}")
        try:
            validated_params = tool.input_schema.model_validate(params)
            return await tool.execute(validated_params, context)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
