"""Unit tests for runner metric aggregation and RunResult properties.

Note: run_agent_scenario / _run_opencode_turn spawn subprocesses and are
covered by integration tests, not unit tests.
"""
import pytest
from unittest.mock import MagicMock, patch
from src.harness.runner import RunResult, run_model_scenario
from src.harness.scenario import Scenario


def make_result(**kwargs) -> RunResult:
    defaults = dict(
        scenario_name="test",
        model_name="test-model",
        provider="test",
        agent_server=None,
        start_time=0.0,
        end_time=10.0,
    )
    defaults.update(kwargs)
    return RunResult(**defaults)


def make_scenario(**kwargs) -> Scenario:
    defaults = dict(
        name="test", category="coding", difficulty="easy",
        type="model", description="Test", tags=[], prompt="Say hello.",
    )
    defaults.update(kwargs)
    return Scenario(**defaults)


# ── RunResult computed properties ─────────────────────────────────────────────

def test_total_time():
    r = make_result(start_time=100.0, end_time=115.5)
    assert r.total_time == pytest.approx(15.5)


def test_tokens_per_second_normal():
    r = make_result(start_time=0.0, end_time=10.0, output_tokens=200)
    assert r.tokens_per_second == pytest.approx(20.0)


def test_tokens_per_second_zero_time():
    r = make_result(start_time=5.0, end_time=5.0, output_tokens=100)
    assert r.tokens_per_second == 0.0


def test_tokens_per_second_no_tokens():
    r = make_result(start_time=0.0, end_time=10.0, output_tokens=0)
    assert r.tokens_per_second == 0.0


def test_error_defaults_false():
    r = make_result()
    assert r.error is False
    assert r.error_message is None


def test_cost_defaults_zero():
    r = make_result()
    assert r.cost_usd == 0.0


def test_follow_up_prompts_default():
    r = make_result()
    assert r.follow_up_prompts == 0


# ── run_model_scenario ────────────────────────────────────────────────────────

def _mock_response(usage: dict, status: int = 200) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = {"usage": usage}
    resp.raise_for_status.return_value = None
    resp.status_code = status
    return resp


@patch("src.harness.runner.httpx.post")
def test_run_model_scenario_tokens(mock_post):
    mock_post.return_value = _mock_response(
        {"prompt_tokens": 10, "completion_tokens": 25, "total_tokens": 35}
    )
    result = run_model_scenario(make_scenario(), "gpt-4o", "openai", "http://localhost")
    assert result.input_tokens == 10
    assert result.output_tokens == 25
    assert result.total_tokens == 35
    assert not result.error


@patch("src.harness.runner.httpx.post")
def test_run_model_scenario_records_agent_server(mock_post):
    mock_post.return_value = _mock_response({"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15})
    result = run_model_scenario(make_scenario(), "llama3", "local", "http://localhost", agent_server="ollama")
    assert result.agent_server == "ollama"
    assert result.provider == "local"


@patch("src.harness.runner.httpx.post")
def test_run_model_scenario_http_error_sets_error_flag(mock_post):
    mock_post.side_effect = Exception("connection refused")
    result = run_model_scenario(make_scenario(), "gpt-4o", "openai", "http://localhost")
    assert result.error is True
    assert "connection refused" in result.error_message


@patch("src.harness.runner.httpx.post")
def test_run_model_scenario_timing(mock_post):
    mock_post.return_value = _mock_response({"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2})
    result = run_model_scenario(make_scenario(), "gpt-4o", "openai", "http://localhost")
    assert result.total_time > 0
    assert result.end_time > result.start_time


