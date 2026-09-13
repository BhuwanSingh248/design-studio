"""Base tool interfaces and standardized execution payloads."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from pydantic import BaseModel


@dataclass
class ToolContext:
    workspace_id: str
    canvas_id: str


@dataclass
class ToolResult:
    success: bool
    data: Any = None
    error: str | None = None


class BaseTool(ABC):
    name: str
    description: str
    parameters_schema: type[BaseModel]

    @abstractmethod
    async def execute(self, params: BaseModel, context: ToolContext) -> ToolResult:
        pass
