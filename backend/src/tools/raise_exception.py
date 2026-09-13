from groq import APIStatusError

from src.core.exception import (
    LLMServiceError,
    LLMRateLimitError,
    LLMAuthenticationError,
    LLMTimeoutError,
    LLMConfigurationError,
)


def raise_llm_exception(exception: APIStatusError):
    status_code = exception.status_code
    message = str(exception)

    if status_code in (401, 403):
        raise LLMAuthenticationError(message)

    if status_code == 429:
        raise LLMRateLimitError(message)

    if status_code in (408,):
        raise LLMTimeoutError(message)

    if status_code == 400:
        raise LLMConfigurationError(message)

    if 500 <= status_code <= 599:
        raise LLMServiceError(message)

    raise LLMServiceError(message)