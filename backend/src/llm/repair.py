"""Fallback schema repair service using LLM feedback."""
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class SchemaRepairService:
    async def repair(self, malformed_json: str, schema: Type[T], error_trace: str) -> T:
        """Prompt LLM to repair invalid JSON matching schema."""
        raise NotImplementedError("Schema repair service to be implemented in Phase 2")
