# Agent Testbench Project Review - 2026-05-25

## Scope

Reviewed the required project contract files, current working tree, API, harness, CLI, web, DB migrations, Docker Compose, and validation commands. I did not read `.env` to avoid exposing local secrets.

Current repo state during review:

- Branch: `main`, up to date with `origin/main`, locally ahead by 14 commits.
- Existing uncommitted work: API run detail/output fields, harness recorder output text, web dependencies/config/styles, new web UI files, and `db/migrations/004_add_output_text.sql`.

## Summary

The project has a sensible monorepo split and the core direction is good: scenarios as Markdown, API as the single DB write surface, Go CLI for deployable recording, Python harness for execution, and a React dashboard. Unit coverage is already useful, and the API/harness/suite concepts are converging.

The main quality risk is that several layers are currently out of sync. The web runtime is broken, the new dashboard is not routed into the app, live-stack tests still use an old run payload, and the harness is bypassing the CLI even though the documented data path says harness -> CLI -> API. These are fixable, but they should be addressed before more feature work piles on top.

## Findings

### P0 - Web server crashes at startup with Express 5

Evidence:

- `web/package.json` uses `express` `^5.2.1`.
- `web/server.js:12` registers `app.get('*', ...)`.
- Running `node server.js` after `make build` failed immediately with:

```text
PathError [TypeError]: Missing parameter name at index 1: *
originalPath: '*'
```

Impact:

The web container will crash on startup, so Docker Compose cannot serve the dashboard even though the static build succeeds.

Recommended fix:

Use an Express 5-compatible catch-all route, such as `/{*splat}`, or switch to a middleware fallback that does not use the invalid wildcard route. Add a lightweight server startup smoke test so this does not regress.

### P1 - Dashboard pages exist but are not reachable

Evidence:

- `web/src/main.tsx:4-8` renders only `App`.
- `web/src/App.tsx:1-122` is still the Vite starter page with Vite/React assets and "Get started" copy.
- `web/src/pages/RunsList.tsx` and `web/src/pages/RunDetail.tsx` are present but not imported by `App` or wrapped in a router.
- `make build` output includes Vite/React assets, confirming the production bundle is still the starter UI.

Impact:

The product's acceptance path says "API persists -> web displays", but the built web app does not display runs or run details.

Recommended fix:

Replace the starter `App` with `BrowserRouter`/routes for `/runs` and `/runs/:id`, redirect `/` to `/runs`, and update/remove the starter CSS/assets/tests. Add tests that assert the runs list route renders and fetches data.

### P1 - Smoke and integration tests post stale run payloads

Evidence:

- `api/src/api/routes/runs.py:7-8` requires `run_name`, `scenario_name`, `model_name`, `provider`, `start_datetime`, `end_datetime`, and `total_time`.
- `tests/integration/test_runs.py:3-8` defines `VALID_RUN` with only the first four fields.
- `tests/integration/test_runs.py:21-36` still expects those minimal payloads to return `201`.
- `tests/smoke/smoke.sh:37-42` posts the same minimal payload and expects `201`.

Impact:

The live-stack integration and smoke checks will fail against the current API. This also weakens the "Done" status for integration/smoke validation in `TODO.md`.

Recommended fix:

Update the smoke and integration payloads to include realistic timestamps and `total_time`, or deliberately loosen API requirements if the intended contract is partial run creation. The stricter API contract is probably the better direction.

### P1 - Agent timeout/stall kills can be recorded as successful runs

Evidence:

- `harness/src/harness/runner.py:94-98` kills the OpenCode process after stdout silence.
- `harness/src/harness/runner.py:101-104` kills it at the hard timeout.
- `harness/src/harness/runner.py:144-145` treats return code `-9` as acceptable instead of raising an error.
- `run_agent_scenario` only sets `result.error = True` when `_run_opencode_turn` raises.

Impact:

A stalled or timed-out agent can produce a `RunResult` with `error=False` and partial output, then get recorded as a normal run. That corrupts benchmark metrics and pass/fail analysis.

Recommended fix:

Track kill reason explicitly and raise on watchdog/hard-timeout kills. Only return success on process code `0`. Capture stderr in the error message, and add a unit test around a mocked killed process or a small subprocess fixture.

### P2 - Root lint misses frontend lint, and frontend lint currently fails

Evidence:

- `Makefile:64-73` defines `lint` as `lint-api lint-harness lint-cli`; there is no `lint-web`.
- `npm run lint` in `web/` fails with `react-hooks/set-state-in-effect` errors at `web/src/pages/RunsList.tsx:32-38` and `web/src/pages/RunDetail.tsx:26-32`.
- `make lint` passes because it never runs ESLint.

Impact:

Agents can report a clean root lint while the frontend has lint-blocking issues.

Recommended fix:

Add `lint-web` to the root Makefile and either adjust the React data-loading pattern to satisfy the enabled hooks rules or intentionally tune the ESLint rule set for this project.

### P2 - Migration strategy is fragile for existing Postgres volumes

Evidence:

- Compose mounts `./db/migrations` to `/docker-entrypoint-initdb.d` at `compose.yaml:25-27`.
- New API code inserts newer columns such as `output_text` (`api/src/api/routes/runs.py:28`, `api/src/api/routes/runs.py:55`) and `suite_run_id` (`api/src/api/routes/runs.py:29`, `api/src/api/routes/runs.py:62`).

Impact:

Fresh DB volumes will initialize with all migration files, but an existing `db_data` volume created before migrations 002-004 will not automatically get the new columns. The API will then fail at runtime when inserting runs.

Recommended fix:

Add an explicit migration runner for local/dev/stage/prod, or document the required reset path for local MVP work. Long term, use a real migration tool or a startup/deploy migration step.

### P2 - Harness currently bypasses the Go CLI recording path

Evidence:

- Project memory and architecture say the intended data flow is harness -> CLI -> API -> DB.
- `harness/src/harness/recorder.py:37-39` posts directly to `/runs/` with `httpx`.
- `harness/src/harness/suite_runner.py:12` imports that Python recorder and `harness/src/harness/suite_runner.py:86-89` calls it directly.
- The Go CLI still requires `--run-name`, `--scenario`, `--model`, and `--provider` flags at `cli/cmd/record.go:31-34`, so `testbench record --data -` is not yet enough by itself.

Impact:

The project has duplicate recording clients and payload-shaping logic. That makes schema changes more expensive and means the deployable CLI is not actually validated in the suite-run path.

Recommended fix:

Choose one path for MVP. If the documented path is still preferred, have the harness invoke the CLI binary and make `record --data -` capable of accepting the complete payload without redundant flags. If direct API posting is preferred, update the architecture/TODO and consider demoting the CLI to a convenience wrapper.

## Strengths

- The module boundaries are clear and map well to the stated workflow.
- The API uses parameterized SQL and straightforward serialization.
- The suite-run aggregate endpoint is a good fit for the dashboard's comparison workflow.
- Scenario front matter now supports suites and grading criteria, which matches the next planned feature set.
- Unit tests are broad enough to catch many payload and orchestration regressions once the integration contract is updated.

## Validation Run

Commands run:

- `git pull --ff-only` - already up to date.
- `make test` - passed after sandbox escalation for normal uv/npm/go cache writes.
  - API: 27 passed.
  - Harness: 50 passed.
  - CLI: 5 passed.
  - Web: 1 file, 2 tests passed.
- `make build` - passed.
- `make lint` - passed for API, harness, and CLI.
- `npm run lint` from `web/` - failed with 2 React hooks lint errors.
- `node server.js` from `web/` after build - failed with the Express 5 wildcard route error.
- `docker compose config --quiet` - exited 0, but emitted warnings about an unset `local` variable from local environment interpolation. I did not inspect `.env`.

Not run:

- `make test-integration` and `make smoke`, because they require a live stack. Based on source inspection, their POST payloads need updating before they can pass against the current API contract.

## Suggested Next Task Order

1. Fix `web/server.js` Express 5 catch-all and add a startup smoke check.
2. Wire the React dashboard routes into `App` and update web tests.
3. Update smoke/integration run payloads to match the API contract.
4. Fix agent timeout/stall error reporting before relying on benchmark metrics.
5. Add `lint-web` to root `make lint` and address the current web lint errors.
6. Decide whether harness recording should go through the Go CLI or direct API, then update code/docs to match.
