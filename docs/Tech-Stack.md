# Technical Stack

## Runtime And Language

- Language: Python 3.14 (api, cli, harness); TypeScript (web)
- Runtime: Python 3.14 via uv; Node 24 LTS (web)
- Package manager: uv (Python); npm (web)

## Frameworks And Libraries

- Application framework: Flask (api)
- UI framework: React (web)
- Web server: Express + Node 24 LTS
- Reverse proxy: Traefik (TLS termination)
- Database: Postgres 18
- Testing: TBD

## Commands

```bash
# Install Python dependencies (api, cli, harness)
uv sync

# Start development server (api only)
uv run flask run

# Start full local stack
docker compose up

# Run tests
# TBD — fill in once test framework is chosen

# Build (web)
# TBD
```

## Environment

- Required environment variables: TBD — at minimum DB connection string and AI provider API keys
- Local services: Postgres 18, Traefik, Express/Node — all managed by Docker Compose
- Deployment target: Docker Compose (local); dedicated VMs for dev / stage / prod

## Version Notes

- Python 3.14 (managed by uv)
- Node 24 LTS
- Postgres 18
- Traefik — version TBD; handles TLS for the web client
