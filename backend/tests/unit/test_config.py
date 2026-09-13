import pytest
from pydantic import ValidationError

from src.core.config import LLMSettings


def test_valid_settings():
    settings = LLMSettings(
        api_key="test-key",
        model="test-model",
        provider="groq",
        timeout=30,
    )

    assert settings.api_key == "test-key"
    assert settings.model == "test-model"
    assert settings.provider == "groq"
    assert settings.timeout == 30


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(ValidationError):
        LLMSettings(
            _env_file=None,
            model="test-model",
            provider="groq",
            timeout=30,
        )



def test_invalid_timeout():
    with pytest.raises(ValidationError):
        LLMSettings(
            api_key="test-key",
            model="test-model",
            provider="groq",
            timeout=-1,
        )