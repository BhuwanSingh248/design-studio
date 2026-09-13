"""Unit tests for POST /api/v1/chat endpoint."""
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.llm.schemas import DesignIssue, DesignReview
from src.main import app

client = TestClient(app)


def test_chat_endpoint_success():
    fake_review = DesignReview(
        summary="Clean monolithic design",
        issues=[
            DesignIssue(
                severity="low",
                category="cohesion",
                description="UserService could be split",
            )
        ],
    )

    with patch("src.llm.client.LLMClient.chat_structured", new_callable=AsyncMock) as mock_structured:
        mock_structured.return_value = fake_review

        response = client.post("/api/v1/chat", json={"message": "Review my class diagram"})

        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert data["reply"]["summary"] == "Clean monolithic design"
        assert len(data["reply"]["issues"]) == 1
        assert data["reply"]["issues"][0]["severity"] == "low"
        mock_structured.assert_awaited_once_with("Review my class diagram", DesignReview)


def test_chat_endpoint_validation_error():
    # Missing required 'message' field
    response = client.post("/api/v1/chat", json={})
    assert response.status_code == 422
