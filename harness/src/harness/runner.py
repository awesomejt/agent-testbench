"""Harness runner — executes a scenario against a target model and returns raw metrics."""

import json
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from .scenario import Scenario

STALL_TIMEOUT = 90      # seconds of stdout silence
HARD_TIMEOUT = 600      # 10-minute absolute cap
MAX_IDENTICAL_TURNS = 3 # consecutive identical tool calls before declaring a loop


@dataclass
class RunResult:
    scenario_name: str
    model_name: str
    provider: str
    agent_server: str | None
    start_time: float
    end_time: float
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0
    follow_up_prompts: int = 0
    output_text: str = ""
    error: bool = False
    error_message: str | None = None
    pass_fail: str | None = None
    score: float | None = None
    grader_model: str | None = None
    grader_rationale: str | None = None
    suite_run_id: int | None = None
    events: list[dict] = field(default_factory=list)

    @property
    def total_time(self) -> float:
        return self.end_time - self.start_time

    @property
    def tokens_per_second(self) -> float:
        if self.total_time == 0:
            return 0.0
        return self.output_tokens / self.total_time


def run_agent_scenario(scenario: Scenario, model: str, provider: str) -> RunResult:  # pragma: no cover
    """Run an agent-type scenario via opencode run --format json."""
    result = RunResult(
        scenario_name=scenario.name,
        model_name=model,
        provider=provider,
        agent_server=None,
        start_time=time.monotonic(),
        end_time=0.0,
    )

    config = {"permission": {"*": "allow"}, "provider": {"model": model}}

    with tempfile.TemporaryDirectory() as tmpdir:
        Path(tmpdir, "opencode.json").write_text(json.dumps(config))
        try:
            _run_opencode_turn(scenario.prompt, tmpdir, result, session_id=None)
        except Exception as exc:
            result.error = True
            result.error_message = str(exc)

    result.end_time = time.monotonic()
    return result


def _run_opencode_turn(prompt: str, cwd: str, result: RunResult, session_id: str | None) -> str | None:  # pragma: no cover
    cmd = ["opencode", "run", "--format", "json"]
    if session_id:
        cmd += ["--session", session_id, "--continue"]
    cmd.append(prompt)

    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    last_output = time.monotonic()
    captured_session_id = session_id

    def _watchdog():
        while proc.poll() is None:
            if time.monotonic() - last_output > STALL_TIMEOUT:
                proc.kill()
                return
            time.sleep(2)

    timer = threading.Thread(target=_watchdog, daemon=True)
    hard_deadline = threading.Timer(HARD_TIMEOUT, proc.kill)
    timer.start()
    hard_deadline.start()

    tool_call_hashes: list[int] = []
    text_parts: list[str] = []

    try:
        for line in proc.stdout:
            last_output = time.monotonic()
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            result.events.append(event)

            if not captured_session_id and event.get("sessionID"):
                captured_session_id = event["sessionID"]

            if event.get("type") == "text":
                text_parts.append(event.get("part", {}).get("text", ""))

            if event.get("type") == "step_finish":
                tokens = event.get("part", {}).get("tokens", {})
                result.input_tokens += tokens.get("input", 0)
                result.output_tokens += tokens.get("output", 0)
                result.total_tokens += tokens.get("input", 0) + tokens.get("output", 0)
                result.cost_usd += event.get("part", {}).get("cost", 0.0)
                result.follow_up_prompts += 1

            if event.get("type") == "tool_use":
                h = hash(json.dumps(event.get("part", {}).get("state", {}).get("input"), sort_keys=True))
                tool_call_hashes.append(h)
                if len(tool_call_hashes) >= MAX_IDENTICAL_TURNS and len(set(tool_call_hashes[-MAX_IDENTICAL_TURNS:])) == 1:
                    proc.kill()
                    raise RuntimeError("Agent loop detected: identical tool calls repeated")
    finally:
        hard_deadline.cancel()
        proc.wait()

    result.output_text = "\n".join(text_parts).strip()

    if proc.returncode not in (0, -9):
        raise RuntimeError(f"opencode exited with code {proc.returncode}")

    return captured_session_id


def run_model_scenario(scenario: Scenario, model: str, provider: str,
                       base_url: str, api_key: str | None = None,
                       agent_server: str | None = None) -> RunResult:
    """Run a model-type scenario directly against an OpenAI-compatible API."""
    result = RunResult(
        scenario_name=scenario.name,
        model_name=model,
        provider=provider,
        agent_server=agent_server,
        start_time=time.monotonic(),
        end_time=0.0,
    )

    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": scenario.prompt}],
    }

    try:
        resp = httpx.post(f"{base_url}/v1/chat/completions", json=payload, headers=headers, timeout=HARD_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        usage = data.get("usage", {})
        result.input_tokens = usage.get("prompt_tokens", 0)
        result.output_tokens = usage.get("completion_tokens", 0)
        result.total_tokens = usage.get("total_tokens", 0)
        choices = data.get("choices", [])
        if choices:
            result.output_text = choices[0].get("message", {}).get("content", "")
    except Exception as exc:
        result.error = True
        result.error_message = str(exc)

    result.end_time = time.monotonic()
    return result
