"""LLM client abstraction supporting retry and structured output."""
from typing import Type, TypeVar
from pydantic import BaseModel
from src.core.config import LLMSettings, llm_settings
from src.llm.cost_tracker import CostTracker
from groq import AsyncGroq, APIStatusError
import asyncio
T = TypeVar("T", bound=BaseModel)


class LLMClient:
    def __init__(self, settings: LLMSettings | None = None, cost_tracker: CostTracker | None = None, session_id: str | None = None):
        self.settings = settings or llm_settings
        self.cost_tracker = cost_tracker
        self._session_id = session_id
        self._client = AsyncGroq(api_key=self.settings.api_key)


    async def chat(self, messages: list[dict[str,str]], temperature: float = 0.7, stream: bool = False):
        try:
            response = await self._execute_with_retries(
                self._client.chat.completions.create,
                model=self.settings.model,
                messages=messages,
                temperature=temperature,
                stream=stream,
            )
            self.track_cost(response)
            return response
        except Exception as e:
            raise
    
    def track_cost(self, response):
        if not self.cost_tracker or not self._session_id:
            return None
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self.cost_tracker.calculate_cost(
            self.settings.model,
            input_tokens,
            output_tokens,
        )
        self.cost_tracker.record_usage(self._session_id, input_tokens, output_tokens, cost)
        return cost

    def calculate_session_cost(self, session_id:str):
        if self.cost_tracker and self._session_id:
            return self.cost_tracker.get_session_total(session_id)
        return None

    async def chat_structured(self, prompt: str, schema: Type[T]) -> T:
        """Execute chat completion enforcing structured Pydantic schema."""
        raise NotImplementedError("chat_structured to be implemented in Phase 2")

    async def _execute_with_retries(self, func,  *args,  max_retries:int=3,  backoff_factor: float = 0.25,  **kwargs):
        for attempt in range(1, max_retries +1):
            try:
                return await func(*args, **kwargs)
            except APIStatusError as e:        
                if e.status_code not in [429, 500, 503, 504] or attempt == max_retries:
                    raise                
                await asyncio.sleep(backoff_factor * (2 ** (attempt - 1)))