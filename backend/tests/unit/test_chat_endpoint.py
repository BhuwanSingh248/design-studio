"""Unit tests for POST /api/v1/chat endpoint."""
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_chat_endpoint_success():
    fake_response = MagicMock()
    fake_response.choices = [MagicMock(message=MagicMock(content="Design advice reply"))]
    fake_response.usage.total_tokens = 42

    with patch("src.llm.client.LLMClient.chat", new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = fake_response

        response = client.post("/api/v1/chat", json={"message": "Review my class diagram"})

        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "Design advice reply"
        assert data["tokens_used"] == 42
        mock_chat.assert_awaited_once_with(
            messages=[{"role": "user", "content": "Review my class diagram"}],
            temperature=0.7,
        )


def test_chat_endpoint_validation_error():
    # Missing required 'message' field
    response = client.post("/api/v1/chat", json={})
    assert response.status_code == 422
