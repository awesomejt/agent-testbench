"""Unit tests for suite_runner.run_suite orchestration logic."""

import textwrap
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.harness.runner import RunResult
from src.harness.suite_runner import run_suite

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _write_scenario(tmp_path: Path, name: str, suite: str) -> None:
    (tmp_path / f"{name}.md").write_text(textwrap.dedent(f"""\
        ---
        name: {name}
        category: math
        difficulty: easy
        type: model
        description: Test
        tags: []
        suite: {suite}
        grading_criteria: Answer must be correct.
        ---
        What is 1+1?
    """))


def _ok_result(name="s1") -> RunResult:
    return RunResult(
        scenario_name=name, model_name="gpt-4o", provider="openai",
        agent_server=None, start_time=0.0, end_time=5.0,
        start_wall=_NOW, end_wall=_NOW,
        output_text="The answer is 2.",
    )


def _suite_run_response(suite_run_id=1):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"id": suite_run_id}
    return resp


def _finalize_response():
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    return resp


@patch("src.harness.suite_runner.record_run")
@patch("src.harness.suite_runner.grade_run")
@patch("src.harness.suite_runner.run_model_scenario")
@patch("src.harness.suite_runner.httpx.put")
@patch("src.harness.suite_runner.httpx.post")
def test_run_suite_creates_suite_run(mock_post, mock_put, mock_run, mock_grade, mock_record, tmp_path):
    _write_scenario(tmp_path, "s1", "math-exam")
    mock_post.return_value = _suite_run_response(1)
    mock_put.return_value = _finalize_response()
    mock_run.return_value = _ok_result()
    mock_grade.return_value = MagicMock(pass_fail="pass", score=1.0, rationale="Good.")

    run_suite("math-exam", "gpt-4o", "openai", "run-1", tmp_path, "http://api:5000",
              grader_api_key="key")

    mock_post.assert_called_once()
    body = mock_post.call_args.kwargs["json"]
    assert body["suite_name"] == "math-exam"
    assert body["model_name"] == "gpt-4o"


@patch("src.harness.suite_runner.record_run")
@patch("src.harness.suite_runner.grade_run")
@patch("src.harness.suite_runner.run_model_scenario")
@patch("src.harness.suite_runner.httpx.put")
@patch("src.harness.suite_runner.httpx.post")
def test_run_suite_runs_matching_scenarios(mock_post, mock_put, mock_run, mock_grade, mock_record, tmp_path):
    _write_scenario(tmp_path, "s1", "math-exam")
    _write_scenario(tmp_path, "s2", "math-exam")
    _write_scenario(tmp_path, "s3", "other-suite")   # should NOT run
    mock_post.return_value = _suite_run_response()
    mock_put.return_value = _finalize_response()
    mock_run.return_value = _ok_result()
    mock_grade.return_value = MagicMock(pass_fail="pass", score=1.0, rationale="Good.")

    run_suite("math-exam", "gpt-4o", "openai", "run-1", tmp_path, "http://api:5000",
              grader_api_key="key")

    assert mock_run.call_count == 2


@patch("src.harness.suite_runner.record_run")
@patch("src.harness.suite_runner.grade_run")
@patch("src.harness.suite_runner.run_model_scenario")
@patch("src.harness.suite_runner.httpx.put")
@patch("src.harness.suite_runner.httpx.post")
def test_run_suite_grades_each_result(mock_post, mock_put, mock_run, mock_grade, mock_record, tmp_path):
    _write_scenario(tmp_path, "s1", "math-exam")
    mock_post.return_value = _suite_run_response()
    mock_put.return_value = _finalize_response()
    mock_run.return_value = _ok_result()
    mock_grade.return_value = MagicMock(pass_fail="pass", score=0.9, rationale="Correct.")

    run_suite("math-exam", "gpt-4o", "openai", "run-1", tmp_path, "http://api:5000",
              grader_api_key="key")

    mock_grade.assert_called_once()


@patch("src.harness.suite_runner.record_run")
@patch("src.harness.suite_runner.grade_run")
@patch("src.harness.suite_runner.run_model_scenario")
@patch("src.harness.suite_runner.httpx.put")
@patch("src.harness.suite_runner.httpx.post")
def test_run_suite_skips_grading_without_key(mock_post, mock_put, mock_run, mock_grade, mock_record, tmp_path):
    _write_scenario(tmp_path, "s1", "math-exam")
    mock_post.return_value = _suite_run_response()
    mock_put.return_value = _finalize_response()
    mock_run.return_value = _ok_result()

    run_suite("math-exam", "gpt-4o", "openai", "run-1", tmp_path, "http://api:5000",
              grader_api_key=None)

    mock_grade.assert_not_called()


@patch("src.harness.suite_runner.record_run")
@patch("src.harness.suite_runner.grade_run")
@patch("src.harness.suite_runner.run_model_scenario")
@patch("src.harness.suite_runner.httpx.put")
@patch("src.harness.suite_runner.httpx.post")
def test_run_suite_records_each_run(mock_post, mock_put, mock_run, mock_grade, mock_record, tmp_path):
    _write_scenario(tmp_path, "s1", "math-exam")
    _write_scenario(tmp_path, "s2", "math-exam")
    mock_post.return_value = _suite_run_response()
    mock_put.return_value = _finalize_response()
    mock_run.return_value = _ok_result()
    mock_grade.return_value = MagicMock(pass_fail="pass", score=1.0, rationale="Good.")

    run_suite("math-exam", "gpt-4o", "openai", "run-1", tmp_path, "http://api:5000",
              grader_api_key="key")

    assert mock_record.call_count == 2


@patch("src.harness.suite_runner.record_run")
@patch("src.harness.suite_runner.grade_run")
@patch("src.harness.suite_runner.run_model_scenario")
@patch("src.harness.suite_runner.httpx.put")
@patch("src.harness.suite_runner.httpx.post")
def test_run_suite_finalizes_suite_run(mock_post, mock_put, mock_run, mock_grade, mock_record, tmp_path):
    _write_scenario(tmp_path, "s1", "math-exam")
    mock_post.return_value = _suite_run_response(suite_run_id=7)
    mock_put.return_value = _finalize_response()
    mock_run.return_value = _ok_result()
    mock_grade.return_value = MagicMock(pass_fail="pass", score=1.0, rationale="Good.")

    run_suite("math-exam", "gpt-4o", "openai", "run-1", tmp_path, "http://api:5000",
              grader_api_key="key")

    mock_put.assert_called_once()
    assert "/suite-runs/7/finalize" in mock_put.call_args.args[0]


@patch("src.harness.suite_runner.record_run")
@patch("src.harness.suite_runner.grade_run")
@patch("src.harness.suite_runner.run_model_scenario")
@patch("src.harness.suite_runner.httpx.put")
@patch("src.harness.suite_runner.httpx.post")
def test_run_suite_continues_after_record_failure(mock_post, mock_put, mock_run, mock_grade, mock_record, tmp_path):
    _write_scenario(tmp_path, "s1", "math-exam")
    _write_scenario(tmp_path, "s2", "math-exam")
    mock_post.return_value = _suite_run_response()
    mock_put.return_value = _finalize_response()
    mock_run.return_value = _ok_result()
    mock_grade.return_value = MagicMock(pass_fail="pass", score=1.0, rationale="Good.")
    mock_record.side_effect = Exception("network error")

    # Should not raise — record failures are warnings
    run_suite("math-exam", "gpt-4o", "openai", "run-1", tmp_path, "http://api:5000",
              grader_api_key="key")

    assert mock_run.call_count == 2


def test_run_suite_returns_1_when_no_scenarios(tmp_path):
    code = run_suite("nonexistent", "gpt-4o", "openai", "run-1", tmp_path, "http://api:5000")
    assert code == 1
