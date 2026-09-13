"""LLM client abstraction supporting retry and structured output."""
from typing import Type, TypeVar
from pydantic import BaseModel
from src.core.config import LLMSettings, llm_settings
from src.llm.cost_tracker import CostTracker
from groq import AsyncGroq, APIStatusError
from src.tools.raise_exception import raise_llm_exception
import asyncio
T = TypeVar("T", bound=BaseModel)


class LLMClient:
    def __init__(self, settings: LLMSettings | None = None, cost_tracker: CostTracker | None = None, session_id: str | None = None):
        self.settings = settings or llm_settings
        self.cost_tracker = cost_tracker
        self._session_id = session_id
        self._client = AsyncGroq(api_key=self.settings.api_key)


    async def chat(self, messages: list[dict[str,str]], temperature: float = 0.7, stream: bool = False):
        response = await self._execute_with_retries(
            self._client.chat.completions.create,
            model=self.settings.model,
            messages=messages,
            temperature=temperature,
            stream=stream,
        )
        self.track_cost(response)
        return response
    
    def track_cost(self, response):
        if not self.cost_tracker or not self._session_id:
            return None
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = self.cost_tracker.calculate_cost(
            response.model,
            input_tokens,
            output_tokens,
        )
        self.cost_tracker.record_usage(self._session_id, input_tokens, output_tokens, cost)
        return cost

    def calculate_session_cost(self, session_id:str):
        if self.cost_tracker:
            return self.cost_tracker.get_session_total(session_id)
        return None

    async def chat_structured(self, prompt: str, schema: Type[T]) -> T:
        """Execute chat completion enforcing structured Pydantic schema."""

        print(f"[ChatStructured] Structuring response for schema: {schema.__name__}")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert JSON generator. "
                    "Respond with ONLY a valid JSON object that strictly matches the requested schema. "
                    "Do not include markdown code blocks, explanations, or any other text."
                    f" Schema: {schema.model_json_schema()}"
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = await self.chat(messages, temperature=0.7, stream=False)

        response_content = response.choices[0].message.content
        if not response_content:
            raise ValueError("Empty response from LLM")

        response_content = self._normalize_json_str(response_content.strip())
        parsed = schema.model_validate_json(response_content)
        return parsed



    async def _execute_with_retries(self, func,  *args,  max_retries:int=3,  backoff_factor: float = 0.25,  **kwargs):
        retryable_status_codes = (429, 500, 502, 503, 504)
        for attempt in range(1, max_retries +1):
            try:
                return await func(*args, **kwargs)
            except APIStatusError as e:        
                if e.status_code not in retryable_status_codes or attempt == max_retries:
                    raise_llm_exception(e)     
                await asyncio.sleep(backoff_factor * (2 ** (attempt - 1)))

    @staticmethod
    def _normalize_json_str(json_str: str) -> str:
        json_str = json_str.strip()

        if json_str.startswith("```json"):
            json_str = json_str[len("```json"):]
            if json_str.endswith("```"):
                json_str = json_str[:-len("```")]
        elif json_str.startswith("```"):
            json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]

        return json_str.strip()