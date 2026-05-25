"""LLM-as-judge grader — evaluates agent output using claude-opus-4-7."""

import json
from dataclasses import dataclass

import httpx

from .scenario import Scenario

GRADER_MODEL = "claude-opus-4-7"
_API_URL = "https://api.anthropic.com/v1/messages"

_SYSTEM = (
    "You are an expert evaluator for AI agent outputs. "
    "Given a task prompt, grading criteria, and the agent's response, "
    "return ONLY a JSON object with these fields:\n"
    '  "pass_fail": one of "pass", "fail", "partial", or "error"\n'
    '  "score": float 0.0–1.0 (1.0 = perfect, 0.0 = complete failure)\n'
    '  "rationale": one to three sentences explaining your evaluation\n'
    "No other text — JSON only."
)


@dataclass
class GradeResult:
    pass_fail: str
    score: float
    rationale: str


def grade_run(scenario: Scenario, agent_output: str, api_key: str) -> GradeResult:
    """Call claude-opus-4-7 to grade agent_output against scenario criteria."""
    criteria = scenario.grading_criteria or "Evaluate for correctness, completeness, and quality."
    user_msg = (
        f"## Task Prompt\n\n{scenario.prompt}\n\n"
        f"## Grading Criteria\n\n{criteria}\n\n"
        f"## Agent Output\n\n{agent_output or '(no output)'}\n\n"
        "Evaluate and return the JSON grade."
    )

    try:
        resp = httpx.post(
            _API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": GRADER_MODEL,
                "max_tokens": 256,
                "system": _SYSTEM,
                "messages": [{"role": "user", "content": user_msg}],
            },
            timeout=60,
        )
        resp.raise_for_status()
        raw = resp.json()["content"][0]["text"]
        data = json.loads(raw)
        return GradeResult(
            pass_fail=data["pass_fail"],
            score=float(data["score"]),
            rationale=data["rationale"],
        )
    except Exception as exc:
        return GradeResult(pass_fail="error", score=0.0, rationale=f"Grading failed: {exc}")
