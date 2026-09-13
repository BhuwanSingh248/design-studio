"""Unit tests for raise_llm_exception mapping helper."""
import httpx
import pytest
from groq import APIStatusError
from src.core.exception import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMRateLimitError,
    LLMServiceError,
    LLMTimeoutError,
)
from src.tools.raise_exception import raise_llm_exception


def make_error(status_code: int, message: str = "Test Error") -> APIStatusError:
    req = httpx.Request("POST", "https://api.groq.com")
    res = httpx.Response(status_code=status_code, request=req)
    return APIStatusError(message=message, response=res, body=None)


@pytest.mark.parametrize(
    "status_code,expected_cls",
    [
        (401, LLMAuthenticationError),
        (403, LLMAuthenticationError),
        (429, LLMRateLimitError),
        (408, LLMTimeoutError),
        (400, LLMConfigurationError),
        (500, LLMServiceError),
        (502, LLMServiceError),
        (503, LLMServiceError),
        (504, LLMServiceError),
        (599, LLMServiceError),
        (418, LLMServiceError),  # Default fallback
    ],
)
def test_raise_llm_exception_mapping(status_code, expected_cls):
    error = make_error(status_code)
    with pytest.raises(expected_cls) as exc_info:
        raise_llm_exception(error)

    assert exc_info.type is expected_cls
