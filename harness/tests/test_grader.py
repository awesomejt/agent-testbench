"""Unit tests for the grader module."""

import json
from unittest.mock import MagicMock, patch

from src.harness.grader import grade_run, GRADER_MODEL
from src.harness.scenario import Scenario


def make_scenario(**kwargs) -> Scenario:
    defaults = dict(
        name="test", category="math", difficulty="easy",
        type="model", description="Test", tags=[], prompt="What is 2+2?",
        grading_criteria="Answer must be 4.", suites=[],
    )
    defaults.update(kwargs)
    return Scenario(**defaults)


def _mock_response(pass_fail="pass", score=1.0, rationale="Correct.") -> MagicMock:
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {
        "content": [{"text": json.dumps({"pass_fail": pass_fail, "score": score, "rationale": rationale})}]
    }
    return resp


@patch("src.harness.grader.httpx.post")
def test_grade_run_pass(mock_post):
    mock_post.return_value = _mock_response("pass", 1.0, "Perfect answer.")
    result = grade_run(make_scenario(), "The answer is 4.", "test-key")
    assert result.pass_fail == "pass"
    assert result.score == 1.0
    assert result.rationale == "Perfect answer."


@patch("src.harness.grader.httpx.post")
def test_grade_run_fail(mock_post):
    mock_post.return_value = _mock_response("fail", 0.0, "Wrong answer.")
    result = grade_run(make_scenario(), "The answer is 5.", "test-key")
    assert result.pass_fail == "fail"
    assert result.score == 0.0


@patch("src.harness.grader.httpx.post")
def test_grade_run_partial(mock_post):
    mock_post.return_value = _mock_response("partial", 0.5, "Partially correct.")
    result = grade_run(make_scenario(), "Maybe 4?", "test-key")
    assert result.pass_fail == "partial"
    assert result.score == 0.5


@patch("src.harness.grader.httpx.post")
def test_grade_run_uses_grader_model(mock_post):
    mock_post.return_value = _mock_response()
    grade_run(make_scenario(), "4", "test-key")
    call_json = mock_post.call_args.kwargs["json"]
    assert call_json["model"] == GRADER_MODEL


@patch("src.harness.grader.httpx.post")
def test_grade_run_includes_criteria_in_prompt(mock_post):
    mock_post.return_value = _mock_response()
    grade_run(make_scenario(grading_criteria="Must equal 4."), "4", "test-key")
    call_json = mock_post.call_args.kwargs["json"]
    assert "Must equal 4." in call_json["messages"][0]["content"]


@patch("src.harness.grader.httpx.post")
def test_grade_run_no_criteria_uses_default(mock_post):
    mock_post.return_value = _mock_response()
    grade_run(make_scenario(grading_criteria=None), "4", "test-key")
    call_json = mock_post.call_args.kwargs["json"]
    assert "correctness" in call_json["messages"][0]["content"]


@patch("src.harness.grader.httpx.post")
def test_grade_run_api_error_returns_error_grade(mock_post):
    mock_post.side_effect = Exception("network error")
    result = grade_run(make_scenario(), "4", "test-key")
    assert result.pass_fail == "error"
    assert result.score == 0.0
    assert "network error" in result.rationale


@patch("src.harness.grader.httpx.post")
def test_grade_run_malformed_json_returns_error_grade(mock_post):
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {"content": [{"text": "not json at all"}]}
    mock_post.return_value = resp
    result = grade_run(make_scenario(), "4", "test-key")
    assert result.pass_fail == "error"


@patch("src.harness.grader.httpx.post")
def test_grade_run_score_is_float(mock_post):
    mock_post.return_value = _mock_response(score=1)  # int from JSON
    result = grade_run(make_scenario(), "4", "test-key")
    assert isinstance(result.score, float)
