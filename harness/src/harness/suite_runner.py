"""Suite runner — execute all scenarios in a named suite, grade, and record results."""

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .grader import GRADER_MODEL, grade_run
from .recorder import record_run
from .runner import run_agent_scenario, run_model_scenario
from .scenario import load_all


def run_suite(
    suite_name: str,
    model: str,
    provider: str,
    run_label: str,
    scenarios_dir: Path,
    api_url: str,
    model_base_url: str = "",
    model_api_key: str | None = None,
    grader_api_key: str | None = None,
    agent_server: str | None = None,
) -> int:
    """Run every scenario in suite_name, grade each, record to API. Returns exit code."""
    scenarios = [s for s in load_all(scenarios_dir) if suite_name in s.suites]
    if not scenarios:
        print(f"error: no scenarios found for suite '{suite_name}'", file=sys.stderr)
        return 1

    print(f"Suite '{suite_name}': {len(scenarios)} scenario(s) — model={model} provider={provider}")

    start_wall = datetime.now(timezone.utc)
    resp = httpx.post(
        f"{api_url}/suite-runs/",
        json={
            "suite_name":    suite_name,
            "run_label":     run_label,
            "model_name":    model,
            "provider":      provider,
            "agent_server":  agent_server,
            "start_datetime": start_wall.isoformat(),
        },
        timeout=30,
    )
    resp.raise_for_status()
    suite_run_id: int = resp.json()["id"]
    print(f"Created suite_run id={suite_run_id}")

    errors = 0
    for scenario in scenarios:
        print(f"  Running: {scenario.name} (type={scenario.type})", end=" ", flush=True)

        if scenario.type == "agent":
            result = run_agent_scenario(scenario, model, provider)  # pragma: no cover
        else:
            result = run_model_scenario(
                scenario, model, provider,
                base_url=model_base_url,
                api_key=model_api_key,
                agent_server=agent_server,
            )

        if result.error:
            print(f"[error] {result.error_message}")
            errors += 1
        else:
            print(f"[ok] {result.total_time:.1f}s {result.output_tokens} tokens", end=" ")

            if grader_api_key and result.output_text:
                grade = grade_run(scenario, result.output_text, grader_api_key)
                result.pass_fail = grade.pass_fail
                result.score = grade.score
                result.grader_model = GRADER_MODEL
                result.grader_rationale = grade.rationale
                print(f"grade={grade.pass_fail} score={grade.score:.2f}")
            else:
                print()

        result.suite_run_id = suite_run_id

        try:
            record_run(result, run_label, api_url)
        except Exception as exc:
            print(f"    [warning] record failed: {exc}", file=sys.stderr)

    httpx.put(f"{api_url}/suite-runs/{suite_run_id}/finalize", timeout=30).raise_for_status()
    print(f"Suite complete. suite_run_id={suite_run_id} errors={errors}")
    return 0 if errors == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a testbench scenario suite")
    parser.add_argument("suite", help="Suite name to run (matches scenario suite: field)")
    parser.add_argument("--model",           required=True, help="Model name")
    parser.add_argument("--provider",        required=True, help="Provider (openai, anthropic, local, …)")
    parser.add_argument("--run-label",       required=True, help="Human-readable label for this run")
    parser.add_argument("--scenarios-dir",   default=os.environ.get("TESTBENCH_SCENARIOS_DIR", "scenarios"),
                        help="Path to scenarios directory (default: scenarios)")
    parser.add_argument("--api-url",         default=os.environ.get("TESTBENCH_API_URL", "http://localhost:5000"),
                        help="Testbench API base URL")
    parser.add_argument("--model-base-url",  default=os.environ.get("TESTBENCH_MODEL_BASE_URL", ""),
                        help="OpenAI-compatible base URL for model scenarios")
    parser.add_argument("--model-api-key",   default=os.environ.get("TESTBENCH_MODEL_API_KEY"),
                        help="API key for the model provider")
    parser.add_argument("--grader-api-key",  default=os.environ.get("ANTHROPIC_API_KEY"),
                        help="Anthropic API key for the grader (defaults to ANTHROPIC_API_KEY env var)")
    parser.add_argument("--agent-server",    default=None, help="Local agent server name (e.g. ollama)")

    args = parser.parse_args()

    sys.exit(run_suite(
        suite_name=args.suite,
        model=args.model,
        provider=args.provider,
        run_label=args.run_label,
        scenarios_dir=Path(args.scenarios_dir),
        api_url=args.api_url,
        model_base_url=args.model_base_url,
        model_api_key=args.model_api_key,
        grader_api_key=args.grader_api_key,
        agent_server=args.agent_server,
    ))


if __name__ == "__main__":
    main()
