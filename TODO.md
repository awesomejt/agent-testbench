# Project TODO

Task list for Agent Testbench, organized by ownership and project phase.

## Needs Attention

Items here require Jason's input before agent work can continue.

- [ ] **Harness invocation model** — Research how to drive OpenCode from a shell script for multi-turn scenarios, stall/timeout detection, and process restart on failure. Confirm the approach before implementing `harness/`. See open questions in `MEMORY.md`.

## Manual Validation

- [ ] Confirm Docker Compose + Traefik TLS setup works on local dev machine
- [ ] Validate deployment workflow to dev / stage / prod VMs
- [ ] Confirm credentials and API keys for AI providers are available and not committed

## AI Agent Work

### Discovery

- [x] **Research: OpenCode harness invocation** — Completed 2026-05-25. Findings in `MEMORY.md` → Harness Design.
- [ ] Inventory existing source, tests, and configs once scaffolding begins

### Planning

- [x] Fill in `docs/Requirements.md`
- [x] Fill in `docs/Tech-Stack.md`
- [x] Fill in `docs/Architecture.md`
- [x] Update `docs/Implementation.md` with implementation phases
- [ ] Finalize DB schema (run record table, reference tables if needed)
- [ ] Finalize API route design (POST /runs, GET /runs with filters)
- [ ] Draft Docker Compose service definitions

### Implementation

- [ ] Scaffold monorepo structure: `scenarios/`, `api/`, `web/`, `cli/`, `harness/`, `db/`
- [ ] `db/` — initial schema and migration (run records table)
- [ ] `api/` — Flask app skeleton + POST /runs endpoint
- [ ] `cli/` — record a run result and post to API
- [ ] `harness/` — run one scenario against one agent and invoke CLI
- [ ] `web/` — React app skeleton + run list view
- [ ] Docker Compose stack with api, web, db, Traefik
- [ ] End-to-end smoke test: scenario → harness → CLI → API → DB → web

### Tests And Quality

- [ ] Add unit tests for API route logic
- [ ] Add integration test for the CLI → API → DB path
- [ ] Confirm lint, type check, and build pass for all modules
- [ ] Review with `QUALITY_CHECKLIST.md`

### Documentation And Deployment

- [ ] Document environment variables (DB URL, AI provider keys)
- [ ] Document Docker Compose startup and teardown
- [ ] Document dev / stage / prod deployment steps
- [ ] Update `README.md` with setup and usage instructions

## In Progress

- [ ]

## Blocked

- [ ]

## Done

- [x] Initial project documentation (PROJECT_BRIEF.md, MEMORY.md, TODO.md, docs/, CLAUDE.md) — 2026-05-25
