"""Unit tests for recorder.record_run."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from src.harness.recorder import record_run
from src.harness.runner import RunResult

_NOW = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
_LATER = datetime(2026, 1, 1, 0, 0, 10, tzinfo=timezone.utc)


def make_result(**kwargs) -> RunResult:
    defaults = dict(
        scenario_name="s1", model_name="gpt-4o", provider="openai",
        agent_server=None, start_time=0.0, end_time=10.0,
        start_wall=_NOW, end_wall=_LATER,
        input_tokens=10, output_tokens=20, total_tokens=30,
        output_text="Hello!",
    )
    defaults.update(kwargs)
    return RunResult(**defaults)


def _mock_post(response_data: dict):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = response_data
    return resp


@patch("src.harness.recorder.httpx.post")
def test_record_run_posts_to_runs_endpoint(mock_post):
    mock_post.return_value = _mock_post({"id": 1})
    record_run(make_result(), "my-run", "http://api:5000")
    assert mock_post.call_args.args[0] == "http://api:5000/runs/"


@patch("src.harness.recorder.httpx.post")
def test_record_run_includes_required_fields(mock_post):
    mock_post.return_value = _mock_post({"id": 1})
    record_run(make_result(), "my-run", "http://api:5000")
    payload = mock_post.call_args.kwargs["json"]
    assert payload["run_name"] == "my-run"
    assert payload["scenario_name"] == "s1"
    assert payload["model_name"] == "gpt-4o"
    assert payload["provider"] == "openai"
    assert payload["total_time"] == 10.0


@patch("src.harness.recorder.httpx.post")
def test_record_run_serializes_wall_times(mock_post):
    mock_post.return_value = _mock_post({"id": 1})
    record_run(make_result(), "my-run", "http://api:5000")
    payload = mock_post.call_args.kwargs["json"]
    assert "2026-01-01" in payload["start_datetime"]
    assert "2026-01-01" in payload["end_datetime"]


@patch("src.harness.recorder.httpx.post")
def test_record_run_includes_grading_fields(mock_post):
    mock_post.return_value = _mock_post({"id": 1})
    result = make_result(pass_fail="pass", score=0.9, grader_model="claude-opus-4-7",
                         grader_rationale="Good.", suite_run_id=42)
    record_run(result, "my-run", "http://api:5000")
    payload = mock_post.call_args.kwargs["json"]
    assert payload["pass_fail"] == "pass"
    assert payload["score"] == 0.9
    assert payload["grader_model"] == "claude-opus-4-7"
    assert payload["suite_run_id"] == 42


@patch("src.harness.recorder.httpx.post")
def test_record_run_includes_agent_server(mock_post):
    mock_post.return_value = _mock_post({"id": 1})
    record_run(make_result(agent_server="ollama"), "my-run", "http://api:5000")
    payload = mock_post.call_args.kwargs["json"]
    assert payload["agent_server"] == "ollama"


@patch("src.harness.recorder.httpx.post")
def test_record_run_includes_error_message_when_set(mock_post):
    mock_post.return_value = _mock_post({"id": 1})
    result = make_result(error=True, error_message="timeout")
    record_run(result, "my-run", "http://api:5000")
    payload = mock_post.call_args.kwargs["json"]
    assert payload["error"] is True
    assert payload["error_message"] == "timeout"


@patch("src.harness.recorder.httpx.post")
def test_record_run_returns_api_response(mock_post):
    mock_post.return_value = _mock_post({"id": 7, "run_name": "my-run"})
    result = record_run(make_result(), "my-run", "http://api:5000")
    assert result["id"] == 7


@patch("src.harness.recorder.httpx.post")
def test_record_run_null_wall_times_passed_as_none(mock_post):
    mock_post.return_value = _mock_post({"id": 1})
    record_run(make_result(start_wall=None, end_wall=None), "my-run", "http://api:5000")
    payload = mock_post.call_args.kwargs["json"]
    assert payload["start_datetime"] is None
    assert payload["end_datetime"] is None
