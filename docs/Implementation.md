# Implementation Plan

## Discovery (Current)

- [x] Confirm project identity, purpose, and module structure
- [x] Document tech stack (Python 3.14 / Flask / uv, TypeScript / React / Node 24, Postgres 18, Docker Compose, Traefik)
- [ ] Confirm scenario file format
- [ ] Confirm web package manager (npm / pnpm / bun)
- [ ] Confirm which AI agents / models are in scope
- [ ] Confirm additional metrics fields (model name, provider, cost, token counts, etc.)
- [ ] Confirm harness tooling (OpenCode integration details)

## Planning

- [ ] Finalize scenario file format and schema
- [ ] Finalize DB schema (run record table + any reference tables)
- [ ] Finalize API route design (POST /runs, GET /runs, filters)
- [ ] Finalize CLI interface (flags, input format, output)
- [ ] Draft Docker Compose service definitions

## MVP

- [ ] Scaffold monorepo directory structure (scenarios/, api/, web/, cli/, harness/, db/)
- [ ] Implement DB schema and migrations
- [ ] Implement API: POST /runs endpoint
- [ ] Implement CLI: record a run result and post to API
- [ ] Implement harness: run one scenario against one agent and invoke CLI
- [ ] Implement web: list and detail view for runs
- [ ] Docker Compose stack (api + web + db + Traefik)
- [ ] End-to-end smoke test: scenario → harness → CLI → API → DB → web

## Refinement

- [ ] Harness: multi-agent and multi-scenario batch execution
- [ ] Web: filtering, sorting, and comparison views
- [ ] API: GET /runs with filters (scenario, model, date range)
- [ ] Error handling and partial-run records
- [ ] Dev / stage / prod environment config

## Release

- [ ] Final validation across full stack
- [ ] Document environment variables and deployment steps
- [ ] Record release notes in MEMORY.md
