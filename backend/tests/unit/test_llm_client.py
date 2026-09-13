"""Unit tests for LLMClient abstraction and retry mechanisms."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest
from groq import APIStatusError
from src.core.config import LLMSettings
from src.llm.client import LLMClient
from src.llm.cost_tracker import CostTracker


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


def test_execute_with_retries_immediate_success(mock_settings):
    """Verify that a successful function call returns immediately on attempt 1."""
    client = LLMClient(settings=mock_settings)
    mock_func = AsyncMock(return_value="success_data")

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = asyncio.run(client._execute_with_retries(mock_func, "arg1", key="val"))

        assert result == "success_data"
        mock_func.assert_awaited_once_with("arg1", key="val")
        mock_sleep.assert_not_called()


@pytest.mark.parametrize("status_code", [429, 500, 503, 504])
def test_execute_with_retries_transient_status_codes_retry_and_succeed(mock_settings, status_code):
    """Verify that retryable HTTP status codes (429, 500, 503, 504) are retried."""
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
    """Verify that when max_retries is reached, the final APIStatusError is raised."""
    client = LLMClient(settings=mock_settings)
    err503 = make_api_status_error(503, message="Service Unavailable")
    mock_func = AsyncMock(side_effect=err503)

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(APIStatusError) as exc_info:
            asyncio.run(
                client._execute_with_retries(mock_func, max_retries=3, backoff_factor=0.1)
            )

        assert exc_info.value.status_code == 503
        assert mock_func.await_count == 3
        # 3 attempts means 2 sleeps before the final failure
        assert mock_sleep.await_count == 2


@pytest.mark.parametrize("non_retryable_code", [400, 401, 403, 404, 422])
def test_execute_with_retries_non_retryable_status_codes_fail_immediately(mock_settings, non_retryable_code):
    """Verify non-retryable errors (e.g. 401 Unauthorized, 400 Bad Request) fail immediately."""
    client = LLMClient(settings=mock_settings)
    error = make_api_status_error(non_retryable_code)
    mock_func = AsyncMock(side_effect=error)

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(APIStatusError) as exc_info:
            asyncio.run(
                client._execute_with_retries(mock_func, max_retries=3)
            )

        assert exc_info.value.status_code == non_retryable_code
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


def test_chat_method_retries_and_tracks_cost(mock_settings, mock_cost_tracker):
    """Verify chat() leverages retry loop and records cost upon success."""
    client = LLMClient(
        settings=mock_settings,
        cost_tracker=mock_cost_tracker,
        session_id="session-42",
    )

    fake_response = MagicMock()
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
    """Verify chat() propagates non-retryable errors directly."""
    client = LLMClient(settings=mock_settings)
    error_401 = make_api_status_error(401, message="Invalid API Key")
    client._client.chat.completions.create = AsyncMock(side_effect=error_401)

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(APIStatusError) as exc_info:
            asyncio.run(
                client.chat(messages=[{"role": "user", "content": "Hi"}])
            )

        assert exc_info.value.status_code == 401
        assert client._client.chat.completions.create.await_count == 1
        mock_sleep.assert_not_called()


def test_chat_without_cost_tracker(mock_settings):
    client = LLMClient(settings=mock_settings)

    fake_response = MagicMock()
    fake_response.usage.prompt_tokens = 10
    fake_response.usage.completion_tokens = 20

    client._client.chat.completions.create = AsyncMock(
        return_value=fake_response
    )

    response = asyncio.run(
        client.chat(
            messages=[{"role": "user", "content": "Hi"}]
        )
    )

    assert response == fake_response