# Project Memory

Persistent project memory for Agent Testbench.

Agents should update this file after meaningful decisions, milestones, blockers, research findings, or implementation runs.

## Current Status

- Current phase: MVP
- Last major milestone: Docker Compose stack complete with Dockerfiles (2026-05-25)
- Next recommended task: Wire CLI → API → DB end-to-end (real DB insert in POST /runs)
- Current blocker: None

## Key Decisions

- **CLI → API → DB** (not CLI → DB directly). The API is the single write path for run records, keeping schema migration in one place.
- **uv** manages Python for api and harness — Python 3.14 baseline.
- **CLI is Go** (Cobra + Viper), not Python. Compiles to a static binary (`make build-linux` → `cli/builds/testbench-linux-amd64`) for clean deployment to test VMs. `builds/` is gitignored.
- **Root Makefile** delegates `test`, `build`, `lint`, `clean` across all modules. CLI has its own `cli/Makefile`.
- **compose.yaml** (v2 syntax, no `version:` key) is the single local dev stack file. Services: traefik, db, api, web. Hostnames: `testbench.local` (web), `api.testbench.local` (api). Requires `/etc/hosts` entries on local dev machine.
- **Web container** uses a two-stage Docker build: Vite builds React → Express (`server.js`) serves `dist/` with SPA catch-all. `VITE_API_URL` is a build arg so the API URL is baked in at image build time.
- **Gunicorn** serves the Flask API inside Docker (2 workers). Flask dev server is for local `uv run flask run` only.
- **npm** is the web package manager.
- **Traefik** handles TLS for the web client in all environments (local dev included).
- **Scenarios are Markdown files** with YAML front matter. The harness discovers them from the filesystem; adding a scenario requires no code change.
- **No multi-user auth** — local / internal use only (Jason only).
- **AI targets: both cloud and local models.** Cloud: Anthropic, OpenAI, Google. Local: Ollama, vLLM, llama.cpp, LM Studio, ONNX Runtime.
- **Cost for local models** is estimated via power consumption (not API billing).
- **Metrics confirmed:** run_name, scenario_name, start/end datetime, total_time, tokens_per_second, follow_up_prompts, model_name, provider, agent_server, input/output/total tokens, cost_usd, pass/fail/score, error, error_message.
- **Two harness invocation paths based on scenario `type` field:**
  - `type: model` — all models (local and cloud) called via direct OpenAI-compatible API. Measures raw speed and quality with no agent overhead. Fair comparison across all models.
  - `type: agent` — all models routed through OpenCode with the target model configured as its provider. Measures real-world agentic performance. Fair because overhead is identical for all models. OpenCode supports local models (Ollama, LM Studio, vLLM) as providers.
- **Per-run temp working directory:** the harness creates a `tempfile.TemporaryDirectory()` per OpenCode run, writes `opencode.json` with permissions and provider config, and sets `cwd` to that directory. Keeps runs isolated; no leftover files between runs.
- **Local model cost formula:** `(watts × seconds / 3600) × rate_per_kwh`. Default rate: $0.14/kWh, configurable.
- **Scenario front matter fields:** `name`, `category`, `difficulty`, `type` (`model` or `agent`), `description`, `tags`. Everything else goes in the Markdown body.

## Architecture Notes

- Monorepo: `scenarios/`, `api/`, `web/`, `cli/`, `harness/`, `db/`
- Local dev: Docker Compose (api + web + db + Traefik)
- Dev / Stage / Prod: API and web on dedicated VMs; Postgres on dedicated Postgres VMs

## Technical Notes

- Python 3.14, uv, Flask (api, harness)
- Go 1.26, Cobra + Viper (cli) — compiles to a single static binary for VM deployment
- TypeScript, React, Node 24 LTS, Express, npm (web)
- Postgres 18

## Manual Validation Findings

-

## Harness Design (Researched 2026-05-25)

**Primary invocation: `opencode run --format json` via Python subprocess.**

OpenCode emits NDJSON to stdout. Key events:
- `step_start` / `step_finish` — turn boundaries; `step_finish` contains token counts and cost
- `tool_use` — tool calls (useful for repetition detection)
- `text` — streamed output

Token fields on `step_finish.part`: `tokens.input`, `tokens.output`, `tokens.reasoning`, `tokens.cache.read/write`, `cost` (USD, cloud only).

**Multi-turn:** Capture `sessionID` from first event, then call `opencode run --session $ID --continue "next prompt"` for each subsequent turn. Do NOT use `--continue` alone (races on parallel runs).

**Permission blocking:** The harness generates a temporary `opencode.json` per run (in the temp working directory) containing `"permission": {"*": "allow"}` and the provider/model config for that run. This avoids interactive prompts and keeps each run isolated. No global config needed; the `--yolo` flag pending in OpenCode is unnecessary with this approach.

**Stall / timeout (multi-layer):**
1. Hard wall-clock timeout: 10 min absolute, enforced via `subprocess.run(timeout=)` or `threading.Timer`
2. Output heartbeat: kill if stdout silent for 90 s (reset on any new NDJSON line)
3. Repetition detection: if 3+ consecutive `step_finish` events have identical `tool_use` input hashes, the agent is looping — kill and retry with a clarifying prompt
4. Max-turn cap: count `step_finish` events with `reason: "tool-calls"`, kill after N (configurable per scenario)

**Recovery:** Re-queue with clarifying prompt → retry up to N times → mark run as `error` and record `error_message`.

**Local model metrics** (Ollama / llama.cpp / vLLM): call their OpenAI-compatible APIs directly rather than routing through OpenCode. Each returns `usage` (input/output tokens) and timing in the response body or via Prometheus (`/metrics`).

**Alternative: `opencode serve` + Python SDK (`opencode-ai` on PyPI)** — cleaner for multi-turn (no per-call startup cost), but adds server lifecycle management. Worth considering for long benchmark runs.

## Open Questions

- None currently

## Blockers

- None — ready to scaffold

## Agent Run Log

Newest entries first.

### 2026-05-25 — Claude Code (claude-sonnet-4-6) [run 3]

- Task: Docker Compose stack + Dockerfiles
- Files changed: compose.yaml, api/Dockerfile, web/Dockerfile, web/server.js, web/package.json (start script, @types/express), .env.example, MEMORY.md
- Validation: compose.yaml syntax valid; Dockerfiles reviewed; web build chain confirmed (Vite → Express)
- Result: Full local stack definable via `docker compose up`; Traefik TLS on testbench.local / api.testbench.local
- Blockers or follow-up: Requires `/etc/hosts` entries for local dev; next step is wiring POST /runs to real DB insert

### 2026-05-25 — Claude Code (claude-sonnet-4-6) [run 2]

- Task: Monorepo scaffold — all six modules
- Files changed: api/, cli/, harness/, web/, db/, scenarios/, Makefile, cli/Makefile, .gitignore
- Validation: 6 tests passing (2 api, 2 harness, 2 cli); `make test` green; `make build-cli` produces cli/builds/testbench
- Result: Full monorepo skeleton in place; CLI rewritten in Go (Cobra+Viper) for single-binary VM deployment

### 2026-05-25 — Claude Code (claude-sonnet-4-6) [run 1]

- Task: Initial documentation pass from project brief
- Files changed: PROJECT_BRIEF.md, MEMORY.md, TODO.md, docs/Requirements.md, docs/Tech-Stack.md, docs/Architecture.md, docs/Implementation.md, CLAUDE.md
- Validation: N/A (documentation only)
- Result: Documentation complete; all design decisions resolved
- Blockers or follow-up: None
