import json
import sys
import click
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

API_URL = os.getenv("TESTBENCH_API_URL", "http://localhost:5000")


@click.group()
def cli():
    """Testbench CLI — record AI agent test run results."""


@cli.command()
@click.option("--run-name", required=True, help="Human-readable run label")
@click.option("--scenario", required=True, help="Scenario name")
@click.option("--model", required=True, help="Model name (e.g. claude-sonnet-4-6)")
@click.option("--provider", required=True, help="Provider (e.g. anthropic, openai, local)")
@click.option("--data", default=None, help="JSON string of additional fields (or - to read stdin)")
def record(run_name, scenario, model, provider, data):
    """Post a run result to the API."""
    payload = {"run_name": run_name, "scenario_name": scenario, "model_name": model, "provider": provider}
    if data == "-":
        payload.update(json.load(sys.stdin))
    elif data:
        payload.update(json.loads(data))

    resp = httpx.post(f"{API_URL}/runs/", json=payload)
    resp.raise_for_status()
    click.echo(json.dumps(resp.json(), indent=2))
