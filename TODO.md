# Project TODO

Task list for Agent Testbench, organized by ownership and project phase.
Last updated: 2026-05-25

## Needs Attention

Items here require Jason's input before agent work can continue.

- [x] **pass_fail / score population** — Decided 2026-05-25: a second "judge" cloud model grades each run after it completes. See grading tasks in the Implementation section below.
- [ ] **AI provider credentials** — Confirm API keys for target providers (Anthropic, OpenAI, local) are available in the test VM environment and how they should be injected (env vars, secrets manager, `.env` file on the VM).
- [ ] **Prod deployment** — When to promote to prod, and which VM / compose stack receives the prod images.

## Manual Validation

- [ ] Confirm Docker Compose + Traefik TLS works on local dev machine (requires `/etc/hosts` entries for `testbench.local` and `api.testbench.local`)
- [ ] Validate `docker compose --profile test run --rm tests` integration test flow against a live stack
- [ ] Confirm `deploy-prod` target and prod VM are ready before promoting

## AI Agent Work

### Implementation

- [ ] **DB migration 002: grading columns** — `002_add_grading_columns.sql`: add `grader_model TEXT` and `grader_rationale TEXT` to the `runs` table.
- [ ] **DB migration 003: suite support** — `003_add_suite_support.sql`: CREATE TABLE `suite_runs` (id, suite_name, run_label, model_name, provider, agent_server, total_scenarios, passed, failed, partial, error_count, avg_score, total_cost_usd, total_time, start_datetime, end_datetime, created_at); ALTER TABLE runs ADD COLUMN `suite_run_id BIGINT REFERENCES suite_runs(id)`.
- [ ] **`Scenario` dataclass: new fields** — Add `grading_criteria: str | None` and `suites: list[str]` to `harness/src/harness/scenario.py`. Parse `suite:` from front matter as a string or list; parse `grading_criteria:` as a string block.
- [ ] **Grading: `harness/src/harness/grader.py`** — New module. `grade_run(scenario, agent_output, api_key) -> GradeResult` calls `claude-opus-4-7` via the Anthropic API with the scenario prompt + `grading_criteria` + agent output, and parses structured JSON: `{pass_fail: pass|fail|partial|error, score: 0–1, rationale: str}`.
- [ ] **Grading: wire into runner** — After each run in `runner.py`, extract the agent's final text output and call `grade_run`. Attach `pass_fail`, `score`, `grader_model`, and `grader_rationale` to `RunResult`.
- [ ] **`RunResult` fields** — Add `pass_fail`, `score`, `grader_model`, `grader_rationale`, and `suite_run_id` fields to the `RunResult` dataclass.
- [ ] **API: grading + suite fields** — Update `POST /runs/` to accept and persist the new grading and suite fields. Add `POST /suite-runs/` and `GET /suite-runs/` endpoints (create a suite run, list with filters). Add `PUT /suite-runs/{id}/finalize` to compute and store aggregates once all scenario runs are complete.
- [ ] **Harness: suite runner** — New entry point (e.g., `harness/src/harness/suite_runner.py`) that: creates a `suite_run` via `POST /suite-runs/`, iterates matching scenarios, runs each via the runner, grades each, records each run via CLI, then calls finalize. Accept `--suite <name>` and `--model <name>` flags.
- [ ] **Harness → CLI invocation** — After each individual run (and grading), serialize the `RunResult` and pipe it to `testbench record --data -`. This is the last unconnected link in the data pipeline.
- [ ] **CLI: `run-suite` command** — Add a `run-suite` subcommand to the Go CLI that wraps the harness suite runner, passing model/provider/api-url config through.
- [ ] **Grading: update example scenario** — Add `grading_criteria` and `suite` fields to `scenarios/example-hello-world.md` showing the expected format.
- [ ] **Web: suite results view** — Primary view listing suite runs (from `GET /suite-runs/`). Columns: suite name, run label, model, pass rate, avg score, total cost, date. Clicking a suite run drills into its individual scenario results.
- [ ] **Web: runs list view** — Secondary view (or tab) showing individual runs from `GET /runs/`. Columns: scenario, model, provider, total time, tokens/sec, pass/fail, score, cost, date.
- [ ] **Web: run detail view** — Full run details including all token counts, grader rationale, error message if any, and raw event log.
- [ ] **Web: filter controls** — Wire `scenario`, `model`, `provider`, `suite`, `from`, `to` query params into filter inputs above each table.
- [ ] **Harness batch runner** — A top-level entry point (CLI command or script) that iterates over all scenarios in `scenarios/` and runs each against a specified model, collecting results via the harness and recording each via the CLI.
- [ ] **Local cost calculation** — Implement the `(watts × seconds / 3600) × rate_per_kwh` formula in the harness for `type: model` local runs. Rate defaults to `$0.14`; make it configurable via env var or flag.
- [ ] **Fix `.coverage` files in git** — `api/.coverage` and `harness/.coverage` were accidentally committed. Remove from tracking (`git rm --cached`) and add to `.gitignore`.

### Tests And Quality

- [ ] **Integration test: CLI → API → DB** — Add an integration test (in `tests/integration/`) that posts a full run payload via the CLI binary and verifies it appears in `GET /runs/`.
- [ ] **End-to-end smoke test** — Manual or scripted path: load a scenario → run harness → CLI records result → verify row in DB → verify it appears in the web UI.
- [ ] **Web tests** — Add Vitest tests for the runs list and detail components once they exist.
- [ ] **Lint and type-check pass** — Run `make lint` and confirm all modules clean; confirm `tsc -b` passes in `web/`.

### Documentation And Deployment

- [ ] **README.md** — Add setup and usage instructions: prerequisites, `.env` setup, `docker compose up`, how to run a scenario, how to deploy.
- [ ] **Environment variable reference** — Document all env vars (DB, API keys, Harbor, VITE_API_URL) either in `README.md` or a dedicated `docs/Environment.md`.
- [ ] **Deployment runbook** — Document the full deploy workflow: `make deploy-dev`, validate on dev, promote to stage, then prod. Note the `/etc/hosts` or DNS entries required per environment.
- [ ] **QUALITY_CHECKLIST.md review** — Walk through the checklist before tagging a first release.

## In Progress

_(nothing active right now)_

## Blocked

_(nothing blocked right now)_

## Done

- [x] Initial project documentation (PROJECT_BRIEF.md, MEMORY.md, TODO.md, docs/, CLAUDE.md) — 2026-05-25
- [x] Research: OpenCode harness invocation (multi-turn, stall/timeout, loop detection) — 2026-05-25
- [x] Scaffold monorepo: `scenarios/`, `api/`, `web/`, `cli/`, `harness/`, `db/` — 2026-05-25
- [x] `db/` — initial schema: `runs` table with 20 fields, 4 indexes — 2026-05-25
- [x] `api/` — Flask app, `POST /runs/` (DB insert, RETURNING *), `GET /runs/` (5 query filters) — 2026-05-25
- [x] `api/` — unit tests (16 tests, 98% coverage) — 2026-05-25
- [x] `cli/` — Go CLI (Cobra + Viper), `record` command posts to API; builds to `cli/builds/` — 2026-05-25
- [x] `cli/` — unit tests (5 tests, 86% coverage) — 2026-05-25
- [x] `harness/` — `Scenario` loader, `run_agent_scenario` (OpenCode subprocess), `run_model_scenario` (httpx) — 2026-05-25
- [x] `harness/` — unit tests (19 tests, 100% testable coverage) — 2026-05-25
- [x] `web/` — React + Vite scaffold, Vitest + @testing-library setup — 2026-05-25
- [x] Docker Compose stack: Traefik TLS, Postgres 18, api, web, integration test container — 2026-05-25
- [x] Smoke tests (`tests/smoke/smoke.sh`, 5 curl checks) — 2026-05-25
- [x] Integration tests (`tests/integration/`, httpx against live stack) — 2026-05-25
- [x] Root Makefile: build, test, coverage, lint, deploy targets for all modules — 2026-05-25
- [x] Harbor deploy: `deploy-dev`, `deploy-stage`, `deploy-prod` targets with git-SHA + latest tags — 2026-05-25
- [x] Harbor TLS trust: CA certs installed system-wide and in Docker cert store — 2026-05-25
- [x] Images pushed to `harbor.taylor.lan/dev` and `harbor.taylor.lan/stage` — 2026-05-25
- [x] Example scenario: `scenarios/example-hello-world.md` — 2026-05-25
