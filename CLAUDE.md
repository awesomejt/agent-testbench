# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Agent Testbench is a collection of tools for testing and recording AI agents. The repository is currently in template/scaffolding state — `PROJECT_BRIEF.md`, `MEMORY.md`, `TODO.md`, and all `docs/` files contain placeholder values that must be filled in before implementation begins.

## Commands

```bash
# Run all tests
make test

# Run tests for a single module
make test-api
make test-harness
make test-cli

# Build CLI binary → cli/builds/testbench
make build-cli

# Cross-compile CLI for Linux amd64 (deploy target)
cd cli && make build-linux     # → cli/builds/testbench-linux-amd64

# Lint all modules
make lint

# Full local stack
docker compose up

# Per-module dev (from module directory)
uv sync && uv run flask run    # api dev server (requires .env)
uv sync && uv run pytest       # api or harness tests
npm install && npm run dev     # web dev server
```

## Project Architecture

This repository follows a **documentation-first agentic workflow**. The root files form a contract between humans and agents:

| File | Role |
|---|---|
| `PROJECT_BRIEF.md` | Goals, users, constraints, stack preferences |
| `AGENTS.md` | Agent operating rules and priorities |
| `AGENT_WORKFLOW.md` | Step-by-step loop for single-agent and multi-agent runs |
| `TODO.md` | Task lanes: Needs Attention → AI Agent Work → In Progress → Blocked → Done |
| `MEMORY.md` | Persistent decisions, milestones, blockers, and run notes |
| `status.yaml` | Shared state machine for agents and automation |
| `QUALITY_CHECKLIST.md` | Pre-review and pre-release checklist |
| `docs/` | Requirements, tech stack, architecture, implementation plan, diagrams |
| `chats/` | Local-only transcript scratch space (Git-ignored) |

### `status.yaml` State Machine

Agents must read `status.yaml` before every run and update it during work:

- `active` — proceed normally
- `working` — another agent is active; skip this cycle
- `paused` — log wake, do no work
- `blocked` — halt until blocker in `TODO.md` is resolved
- `error` — halt and require human recovery
- `stopped` — project complete or deliberately shut down

Set `working` at start of a task, return to `active` (or `blocked`/`error`) before ending.

### Task Selection Order

When picking from `TODO.md`, prefer:
1. Blocker removal and requirements clarification
2. Failing tests, broken builds, security issues
3. Architecture or scaffolding that unlocks later work
4. Core implementation
5. Tests and validation gaps
6. Docs, deployment, cleanup

### External Log Storage

Transcripts are never committed. Workflow managers mirror logs to:
- Runtime logs: `/var/log/hermes`
- Mirrored logs: `/mnt/hermes/logs`
- Project output and transcripts: `/mnt/hermes/output/<project-name>/`

## Commit Convention

Use Conventional Commits with AI attribution. Activate the template:

```bash
git config commit.template .gitmessage
```

Format: `<type>(scope): <short description>` with `AI-assisted: yes/no` footer fields.

## Initialization Checklist

Before starting implementation work, complete these in order:

1. Fill all `{{PLACEHOLDER}}` values in `PROJECT_BRIEF.md`, `MEMORY.md`, `TODO.md`
2. Fill `docs/Requirements.md` and `docs/Tech-Stack.md`
3. Fill `docs/Architecture.md` and `docs/Implementation.md` (or mark as intentionally simple)
4. Add actual commands to `docs/Tech-Stack.md`
5. Confirm `status.yaml` is `active`
