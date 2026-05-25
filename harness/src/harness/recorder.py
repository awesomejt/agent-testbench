"""Post a completed RunResult to the testbench API."""

import httpx

from .runner import RunResult


def record_run(result: RunResult, run_name: str, api_url: str) -> dict:
    """Serialize result and POST to /runs/. Returns the created run record."""
    payload: dict = {
        "run_name":          run_name,
        "scenario_name":     result.scenario_name,
        "model_name":        result.model_name,
        "provider":          result.provider,
        "start_datetime":    result.start_wall.isoformat() if result.start_wall else None,
        "end_datetime":      result.end_wall.isoformat() if result.end_wall else None,
        "total_time":        result.total_time,
        "tokens_per_second": result.tokens_per_second,
        "follow_up_prompts": result.follow_up_prompts,
        "input_tokens":      result.input_tokens,
        "output_tokens":     result.output_tokens,
        "total_tokens":      result.total_tokens,
        "cost_usd":          result.cost_usd,
        "error":             result.error,
        "pass_fail":         result.pass_fail,
        "score":             result.score,
        "grader_model":      result.grader_model,
        "grader_rationale":  result.grader_rationale,
        "suite_run_id":      result.suite_run_id,
    }
    if result.error_message:
        payload["error_message"] = result.error_message
    if result.agent_server:
        payload["agent_server"] = result.agent_server

    resp = httpx.post(f"{api_url}/runs/", json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()
