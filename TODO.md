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

- [ ] **Grading: DB migration** — Add `002_add_grading_columns.sql`: `grader_model TEXT`, `grader_rationale TEXT` columns to the `runs` table.
- [ ] **Grading: `Scenario` dataclass** — Add optional `grading_criteria: str | None` field to `harness/src/harness/scenario.py` and parse it from the YAML front matter.
- [ ] **Grading: `harness/src/harness/grader.py`** — New module. `grade_run(scenario, agent_output, grader_model, api_key) -> GradeResult` calls `claude-opus-4-7` via the Anthropic API, prompts it with the scenario prompt + criteria + agent output, and parses a structured JSON response: `{pass_fail: pass|fail|partial|error, score: 0–1, rationale: str}`.
- [ ] **Grading: wire into runner** — After each run in `runner.py`, extract the agent's final text output and call `grade_run`. Attach `pass_fail`, `score`, `grader_model`, and `grader_rationale` to `RunResult`.
- [ ] **Grading: `RunResult` fields** — Add `pass_fail`, `score`, `grader_model`, `grader_rationale` fields to the `RunResult` dataclass.
- [ ] **Grading: API + CLI** — Update `POST /runs/` to accept and persist the four new grading fields. CLI `record` command passes them through `--data` already; no CLI changes needed.
- [ ] **Grading: update example scenario** — Add a `grading_criteria` section to `scenarios/example-hello-world.md` showing the expected format.
- [ ] **Harness → CLI invocation** — After `run_agent_scenario` / `run_model_scenario` completes (and grading runs), serialize the `RunResult` and pipe it to `testbench record --data -` so results reach the API and DB. This is the last unconnected link in the data pipeline.
- [ ] **Web: runs list view** — Replace the Vite default scaffold in `web/src/App.tsx` with a paginated table of runs fetched from `GET /runs/`. Columns: run name, scenario, model, provider, total time, tokens/sec, pass/fail, cost, date.
- [ ] **Web: run detail view** — Clicking a row shows full run details including all token counts, error message if any, and raw event log.
- [ ] **Web: filter controls** — Wire the `scenario`, `model`, `provider`, `from`, `to` query params from `GET /runs/` into the UI as filter inputs above the runs table.
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
