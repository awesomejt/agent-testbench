# Project Requirements

## Purpose

Agent Testbench stress-tests AI agent models against standardized prompt scenarios and collects structured performance metrics for comparison across models, runs, and scenarios.

## Users

- Primary user: Jason (solo developer and AI researcher)
- Secondary users: None currently

## Key Features

- **Scenario library** — a collection of Markdown files with YAML front matter (`name`, `category`, `difficulty`, `description`, `tags`, `type`) and a prompt as the body; adding a scenario requires no code change. `type: model` runs direct API (raw speed/quality), `type: agent` runs via OpenCode (real-world agentic performance)
- **Test harness** — executes scenarios against cloud models (Anthropic, OpenAI, Google) and local models (Ollama, vLLM, llama.cpp, LM Studio, ONNX Runtime, etc.); likely OpenCode-based
- **Result recording** — CLI tool accepts structured metric output and posts it to the API or DB
- **Metrics dashboard** — web UI for browsing, filtering, and comparing run results
- **Persistent storage** — Postgres 18 stores all test run records

## Metrics To Capture

| Field | Type | Notes |
|---|---|---|
| `run_name` | string | Human-readable label for the test run |
| `scenario_name` | string | Which scenario was executed |
| `start_datetime` | timestamp | When the run started |
| `end_datetime` | timestamp | When the run ended |
| `total_time` | duration | Elapsed wall-clock time |
| `tokens_per_second` | float | Throughput metric |
| `follow_up_prompts` | int | Number of follow-up turns in the run |
| `model_name` | string | e.g. `claude-sonnet-4-6`, `gpt-4o`, `llama3` |
| `provider` | string | Anthropic, OpenAI, Google, local, etc. |
| `agent_server` | string | For local models: Ollama, vLLM, llama.cpp, LM Studio, ONNX Runtime, etc. Null for cloud. |
| `input_tokens` | int | Prompt token count |
| `output_tokens` | int | Completion token count |
| `total_tokens` | int | Sum of input + output |
| `cost_usd` | decimal | API billing cost for cloud models; for local models: `(watts × seconds / 3600) × rate_per_kwh` — default rate $0.14/kWh, configurable |
| `pass_fail` | enum | `pass`, `fail`, `partial`, `error`, or null if no expected outcome |
| `score` | float | Numeric quality score if applicable; null otherwise |
| `error` | boolean | Whether the run errored |
| `error_message` | string | Error detail if applicable |

## Non-Functional Requirements

- Performance: API and DB should handle concurrent test runs without blocking each other
- Security: No secrets in repo; DB credentials and API keys via environment variables
- Reliability: Run records should be written atomically; partial/failed runs should be distinguishable from successful ones
- Compatibility: Docker Compose for local dev; dedicated Postgres VMs for dev / stage / prod

## Out Of Scope

- Multi-user authentication
- Real-time streaming metrics during a run
- Agent training or fine-tuning

## Acceptance Criteria

- A scenario can be executed end-to-end: harness runs it → CLI records → API persists → web displays
- Metrics are queryable and comparable across runs, scenarios, and models
- New scenarios can be added as files without code changes to the harness or API
