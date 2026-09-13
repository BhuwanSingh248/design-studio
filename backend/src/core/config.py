from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="LLM_",
        extra="ignore",
    )

    api_key: str
    model: str
    provider: str
    timeout: int = Field(default=30, gt=0)
    
llm_settings = LLMSettings()