"""Unit tests for CostTracker."""
import pytest
from src.llm.cost_tracker import CostTracker


@pytest.fixture
def pricing():
    return {
        "gpt-4": {"input": 0.00003, "output": 0.00006},
        "qwen-27b": {"input": 0.00001, "output": 0.00002},
    }


def test_calculate_cost_known_model(pricing):
    tracker = CostTracker(pricing=pricing)
    # 1000 input tokens * 0.00003 = 0.03
    # 500 output tokens * 0.00006 = 0.03
    # Total = 0.06
    cost = tracker.calculate_cost("gpt-4", tokens_input=1000, tokens_output=500)
    assert round(cost, 6) == 0.06


def test_calculate_cost_unknown_model_raises(pricing):
    tracker = CostTracker(pricing=pricing)
    with pytest.raises(ValueError, match="Unknown model: llama-unknown"):
        tracker.calculate_cost("llama-unknown", tokens_input=100, tokens_output=50)


def test_record_usage_and_get_session_total(pricing):
    tracker = CostTracker(pricing=pricing)
    assert tracker.get_session_total("user-1") == {"input": 0, "output": 0, "cost": 0.0}

    tracker.record_usage(user_id="user-1", tokens_input=100, tokens_output=50, cost=0.015)
    total = tracker.get_session_total("user-1")
    assert total["input"] == 100
    assert total["output"] == 50
    assert total["cost"] == 0.015

    # Accumulate second usage
    tracker.record_usage(user_id="user-1", tokens_input=200, tokens_output=100, cost=0.030)
    updated_total = tracker.get_session_total("user-1")
    assert updated_total["input"] == 300
    assert updated_total["output"] == 150
    assert round(updated_total["cost"], 4) == 0.045
