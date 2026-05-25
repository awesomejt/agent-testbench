# Technical Stack

## Runtime And Language

- Language: Python 3.14 (api, harness); Go 1.26 (cli); TypeScript (web)
- Runtime: Python 3.14 via uv; Go toolchain; Node 24 LTS (web)
- Package manager: uv (Python); Go modules; npm (web)

## Frameworks And Libraries

- Application framework: Flask (api)
- CLI framework: Cobra + Viper (cli)
- UI framework: React (web)
- Web server: Express + Node 24 LTS
- Reverse proxy: Traefik (TLS termination)
- Database: Postgres 18
- Testing: pytest (Python); go test (cli)

## Commands

```bash
# Install Python dependencies (api, harness)
uv sync

# Start development server (api only)
uv run flask run

# Start full local stack
docker compose up

# Run tests — Python modules
uv run pytest

# Run tests — CLI
cd cli && go test ./...

# Build CLI binary
cd cli && go build -o testbench .

# Build (web)
cd web && npm run build
```

## Environment

- Required environment variables: TBD — at minimum DB connection string and AI provider API keys
- Local services: Postgres 18, Traefik, Express/Node — all managed by Docker Compose
- Deployment target: Docker Compose (local); dedicated VMs for dev / stage / prod

## Version Notes

- Python 3.14 (managed by uv)
- Go 1.26
- Node 24 LTS
- Postgres 18
- Traefik — version TBD; handles TLS for the web client
