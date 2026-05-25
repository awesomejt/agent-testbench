# Project Brief

## Project Identity

- Project name: `Agent Testbench`
- Short name: `testbench`
- Repository: https://github.com/awesomejt/agent-testbench
- Project type: `full-stack monorepo`
- Primary users: Jason (solo developer / AI researcher)

## Purpose

Stress-test AI agent models against standardized scenarios and record structured performance metrics for comparison across models, runs, and scenarios.

## Success Criteria

The project is successful when:

- A scenario can be executed against an AI agent end-to-end: harness runs it, CLI records results, API persists them, web dashboard displays them.
- Metrics are captured consistently and queryable across runs, scenarios, and models.
- New scenarios can be added without code changes.

## Users And Workflows

- Primary user: Jason
- Secondary users: None currently
- Most important workflow: Run a scenario against a target AI agent and record the results
- Repeated or high-frequency workflow: Browse and compare metrics across runs in the web dashboard
- Admin or maintenance workflow: Add new scenarios; manage or replay DB records

## Must Include

- `scenarios/` — Structured prompt files for AI agent stress tests
- `api/` — Python 3.14 / Flask REST API
- `web/` — TypeScript / React metrics dashboard
- `cli/` — CLI tool for recording test results (used by the harness)
- `harness/` — Test execution engine (likely OpenCode-based)
- `db/` — Postgres 18 schema, migrations, and seed data
- Metrics: tokens per second, total time, follow-up prompt count, run name, scenario name, start/end datetime, model name, provider, agent server, input/output/total token counts, cost (USD; estimated via power consumption for local models), pass/fail or score

## Nice To Include

- Per-run cost tracking (API billing)
- Pass/fail or score field for scenarios with expected outcomes
- Model and provider metadata per run (model name, version, provider)

## Out Of Scope

- Multi-user auth (single user: Jason)
- Real-time streaming metrics during a run
- Agent training or fine-tuning

## Technical Preferences

- Preferred language/runtime: Python 3.14 (api, cli, harness); TypeScript / Node 24 LTS (web)
- Preferred framework: Flask (api); React (web); Express (web server)
- Preferred package manager: uv (Python); npm (web)
- Preferred database/storage: Postgres 18
- Deployment target: Docker Compose (local dev); dedicated VMs for dev, stage, prod
- Authentication requirements: None (local/internal use only)
- Accessibility or browser/device support: Desktop browser, modern evergreen

## Source Material

| Source | Path or URL | How to use it |
| --- | --- | --- |
| | | |

## Validation Needed

- Confirm Docker Compose + Traefik TLS setup works on local dev machine
- Confirm credentials and API keys for AI providers (Anthropic, OpenAI, Google) are available
- Confirm power consumption estimation approach for local model cost simulation
- Validate deployment workflow to dev / stage / prod VMs
