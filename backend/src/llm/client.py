"""LLM client abstraction supporting retry and structured output."""
from typing import Type, TypeVar
from pydantic import BaseModel
from src.core.config import llm_settings
from src.llm.cost_tracker import CostTracker

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    def __init__(self, settings=None):
        self.settings = settings or llm_settings
        self.cost_tracker = CostTracker()

    async def chat(self, prompt: str, temperature: float = 0.7) -> str:
        """Execute simple chat completion."""
        return f"Response for: {prompt}"

    async def chat_structured(self, prompt: str, schema: Type[T]) -> T:
        """Execute chat completion enforcing structured Pydantic schema."""
        raise NotImplementedError("chat_structured to be implemented in Phase 2")
