"""Unit tests for LLMClient abstraction, retry mechanisms, and structured output."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest
from pydantic import BaseModel, ValidationError
from groq import APIStatusError
from src.core.config import LLMSettings
from src.core.exception import (
    LLMAuthenticationError,
    LLMConfigurationError,
    LLMException,
    LLMRateLimitError,
    LLMServiceError,
    LLMTimeoutError,
)
from src.llm.client import LLMClient
from src.llm.cost_tracker import CostTracker
from src.llm.schemas import DesignIssue, DesignReview


def make_api_status_error(status_code: int, message: str = "API Error") -> APIStatusError:
    """Helper to construct a mock Groq APIStatusError with a specific status code."""
    request = httpx.Request("POST", "https://api.groq.com/chat/completions")
    response = httpx.Response(status_code=status_code, request=request)
    return APIStatusError(message=message, response=response, body=None)


@pytest.fixture
def mock_settings():
    return LLMSettings(
        _env_file=None,
        api_key="mock-api-key",
        model="mock-model",
        provider="groq",
        timeout=30,
    )


@pytest.fixture
def mock_cost_tracker():
    pricing = {
        "mock-model": {"input": 0.0001, "output": 0.0002}
    }
    return CostTracker(pricing=pricing)


# ---------------------------------------------------------------------------
# Retry Logic Tests
# ---------------------------------------------------------------------------

def test_execute_with_retries_immediate_success(mock_settings):
    """Verify that a successful function call returns immediately on attempt 1."""
    client = LLMClient(settings=mock_settings)
    mock_func = AsyncMock(return_value="success_data")

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = asyncio.run(client._execute_with_retries(mock_func, "arg1", key="val"))

        assert result == "success_data"
        mock_func.assert_awaited_once_with("arg1", key="val")
        mock_sleep.assert_not_called()


@pytest.mark.parametrize("status_code", [429, 500, 502, 503, 504])
def test_execute_with_retries_transient_status_codes_retry_and_succeed(mock_settings, status_code):
    """Verify that retryable HTTP status codes (429, 500, 502, 503, 504) are retried."""
    client = LLMClient(settings=mock_settings)
    error = make_api_status_error(status_code)
    mock_func = AsyncMock(side_effect=[error, "recovered_data"])

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = asyncio.run(
            client._execute_with_retries(mock_func, max_retries=3, backoff_factor=0.25)
        )

        assert result == "recovered_data"
        assert mock_func.await_count == 2
        mock_sleep.assert_awaited_once_with(0.25)


def test_execute_with_retries_exponential_backoff_progression(mock_settings):
    """Verify exponential backoff calculation across multiple retry attempts."""
    client = LLMClient(settings=mock_settings)
    err429 = make_api_status_error(429)
    err503 = make_api_status_error(503)
    mock_func = AsyncMock(side_effect=[err429, err503, "success"])

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = asyncio.run(
            client._execute_with_retries(mock_func, max_retries=3, backoff_factor=0.5)
        )

        assert result == "success"
        assert mock_func.await_count == 3
        # Attempt 1 -> 2: 0.5 * 2^0 = 0.5s
        # Attempt 2 -> 3: 0.5 * 2^1 = 1.0s
        assert mock_sleep.await_count == 2
        assert mock_sleep.await_args_list[0].args == (0.5,)
        assert mock_sleep.await_args_list[1].args == (1.0,)


def test_execute_with_retries_exhaustion_raises(mock_settings):
    """Verify that when max_retries is reached, the mapped LLMException is raised."""
    client = LLMClient(settings=mock_settings)
    err503 = make_api_status_error(503, message="Service Unavailable")
    mock_func = AsyncMock(side_effect=err503)

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(LLMServiceError):
            asyncio.run(
                client._execute_with_retries(mock_func, max_retries=3, backoff_factor=0.1)
            )

        assert mock_func.await_count == 3
        # 3 attempts means 2 sleeps before the final failure
        assert mock_sleep.await_count == 2


@pytest.mark.parametrize(
    "status_code,expected_exception",
    [
        (400, LLMConfigurationError),
        (401, LLMAuthenticationError),
        (403, LLMAuthenticationError),
        (404, LLMServiceError),
        (408, LLMTimeoutError),
        (422, LLMServiceError),
    ],
)
def test_execute_with_retries_non_retryable_status_codes_fail_immediately(
    mock_settings, status_code, expected_exception
):
    """Verify non-retryable errors fail immediately without retry and raise mapped exceptions."""
    client = LLMClient(settings=mock_settings)
    error = make_api_status_error(status_code)
    mock_func = AsyncMock(side_effect=error)

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(expected_exception):
            asyncio.run(
                client._execute_with_retries(mock_func, max_retries=3)
            )

        # Should not retry at all
        assert mock_func.await_count == 1
        mock_sleep.assert_not_called()


def test_execute_with_retries_non_api_exception_fails_immediately(mock_settings):
    """Verify generic exceptions (ValueError, TypeError, etc.) are not caught by retry loop."""
    client = LLMClient(settings=mock_settings)
    mock_func = AsyncMock(side_effect=ValueError("Invalid model argument"))

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(ValueError, match="Invalid model argument"):
            asyncio.run(
                client._execute_with_retries(mock_func, max_retries=3)
            )

        assert mock_func.await_count == 1
        mock_sleep.assert_not_called()


# ---------------------------------------------------------------------------
# Chat and Cost Tracking Tests
# ---------------------------------------------------------------------------

def test_chat_method_retries_and_tracks_cost(mock_settings, mock_cost_tracker):
    """Verify chat() leverages retry loop and records cost upon success."""
    client = LLMClient(
        settings=mock_settings,
        cost_tracker=mock_cost_tracker,
        session_id="session-42",
    )

    fake_response = MagicMock()
    fake_response.model = "mock-model"
    fake_response.usage.prompt_tokens = 50
    fake_response.usage.completion_tokens = 100
    fake_response.choices = [MagicMock(message=MagicMock(content="Hello world"))]

    error_429 = make_api_status_error(429)
    # Fail on first call, succeed on second call
    client._client.chat.completions.create = AsyncMock(side_effect=[error_429, fake_response])

    with patch("asyncio.sleep", new_callable=AsyncMock):
        response = asyncio.run(
            client.chat(messages=[{"role": "user", "content": "Hi"}])
        )

        assert response == fake_response
        assert client._client.chat.completions.create.await_count == 2

        # Check cost tracking
        session_total = client.calculate_session_cost("session-42")
        assert session_total["input"] == 50
        assert session_total["output"] == 100
        # Cost: (50 * 0.0001) + (100 * 0.0002) = 0.005 + 0.02 = 0.025
        assert round(session_total["cost"], 4) == 0.025


def test_chat_method_unrecoverable_error_raises(mock_settings):
    """Verify chat() propagates non-retryable mapped errors directly."""
    client = LLMClient(settings=mock_settings)
    error_401 = make_api_status_error(401, message="Invalid API Key")
    client._client.chat.completions.create = AsyncMock(side_effect=error_401)

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(LLMAuthenticationError):
            asyncio.run(
                client.chat(messages=[{"role": "user", "content": "Hi"}])
            )

        assert client._client.chat.completions.create.await_count == 1
        mock_sleep.assert_not_called()


def test_chat_without_cost_tracker(mock_settings):
    """Verify chat() operates cleanly when no cost_tracker is supplied."""
    client = LLMClient(settings=mock_settings)

    fake_response = MagicMock()
    fake_response.model = "mock-model"
    fake_response.usage.prompt_tokens = 10
    fake_response.usage.completion_tokens = 20

    client._client.chat.completions.create = AsyncMock(return_value=fake_response)

    response = asyncio.run(
        client.chat(messages=[{"role": "user", "content": "Hi"}])
    )

    assert response == fake_response
    assert client.calculate_session_cost("session-1") is None


# ---------------------------------------------------------------------------
# Structured Output Tests
# ---------------------------------------------------------------------------

class DummySchema(BaseModel):
    name: str
    count: int


def test_chat_structured_success_plain_json(mock_settings):
    """Verify chat_structured parses valid plain JSON into target schema."""
    client = LLMClient(settings=mock_settings)

    fake_response = MagicMock()
    fake_response.model = "mock-model"
    fake_response.usage.prompt_tokens = 10
    fake_response.usage.completion_tokens = 20
    fake_response.choices = [MagicMock(message=MagicMock(content='{"name": "diagram", "count": 3}'))]

    client._client.chat.completions.create = AsyncMock(return_value=fake_response)

    result = asyncio.run(client.chat_structured("Generate dummy", DummySchema))

    assert isinstance(result, DummySchema)
    assert result.name == "diagram"
    assert result.count == 3


@pytest.mark.parametrize(
    "raw_content",
    [
        '```json\n{"name": "fenced_json", "count": 7}\n```',
        '```\n{"name": "fenced_json", "count": 7}\n```',
        '   ```json\n{"name": "fenced_json", "count": 7}\n```   ',
    ],
)
def test_chat_structured_normalizes_markdown_code_blocks(mock_settings, raw_content):
    """Verify chat_structured strips markdown code fences before validating JSON."""
    client = LLMClient(settings=mock_settings)

    fake_response = MagicMock()
    fake_response.model = "mock-model"
    fake_response.usage.prompt_tokens = 10
    fake_response.usage.completion_tokens = 20
    fake_response.choices = [MagicMock(message=MagicMock(content=raw_content))]

    client._client.chat.completions.create = AsyncMock(return_value=fake_response)

    result = asyncio.run(client.chat_structured("Generate dummy", DummySchema))

    assert isinstance(result, DummySchema)
    assert result.name == "fenced_json"
    assert result.count == 7


def test_chat_structured_with_design_review_schema(mock_settings):
    """Verify chat_structured correctly parses the DesignReview domain schema."""
    client = LLMClient(settings=mock_settings)

    json_payload = """
    {
        "summary": "Overall good design with minor coupling",
        "issues": [
            {
                "severity": "medium",
                "category": "coupling",
                "description": "User class directly references DatabaseConnection"
            }
        ]
    }
    """
    fake_response = MagicMock()
    fake_response.model = "mock-model"
    fake_response.usage.prompt_tokens = 25
    fake_response.usage.completion_tokens = 40
    fake_response.choices = [MagicMock(message=MagicMock(content=json_payload))]

    client._client.chat.completions.create = AsyncMock(return_value=fake_response)

    result = asyncio.run(client.chat_structured("Review design", DesignReview))

    assert isinstance(result, DesignReview)
    assert result.summary == "Overall good design with minor coupling"
    assert len(result.issues) == 1
    assert result.issues[0].severity == "medium"
    assert result.issues[0].category == "coupling"


def test_chat_structured_empty_response_raises_value_error(mock_settings):
    """Verify chat_structured raises ValueError when response content is empty."""
    client = LLMClient(settings=mock_settings)

    fake_response = MagicMock()
    fake_response.model = "mock-model"
    fake_response.usage.prompt_tokens = 5
    fake_response.usage.completion_tokens = 0
    fake_response.choices = [MagicMock(message=MagicMock(content=""))]

    client._client.chat.completions.create = AsyncMock(return_value=fake_response)

    with pytest.raises(ValueError, match="Empty response from LLM"):
        asyncio.run(client.chat_structured("Prompt", DummySchema))


def test_chat_structured_invalid_json_raises_validation_error(mock_settings):
    """Verify chat_structured raises ValidationError on invalid JSON schema payload."""
    client = LLMClient(settings=mock_settings)

    fake_response = MagicMock()
    fake_response.model = "mock-model"
    fake_response.usage.prompt_tokens = 10
    fake_response.usage.completion_tokens = 10
    # Missing required 'count' field
    fake_response.choices = [MagicMock(message=MagicMock(content='{"name": "broken"}'))]

    client._client.chat.completions.create = AsyncMock(return_value=fake_response)

    with pytest.raises(ValidationError):
        asyncio.run(client.chat_structured("Prompt", DummySchema))


# ---------------------------------------------------------------------------
# Normalization Helper Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "raw_input,expected",
    [
        ('{"a": 1}', '{"a": 1}'),
        ('```json{"a": 1}```', '{"a": 1}'),
        ('```{"a": 1}```', '{"a": 1}'),
        ('\n```json\n{"a": 1}\n```\n', '{"a": 1}'),
        ('   {"a": 1}   ', '{"a": 1}'),
    ],
)
def test_normalize_json_str(raw_input, expected):
    """Verify _normalize_json_str handles various code fence formatting."""
    assert LLMClient._normalize_json_str(raw_input) == expected