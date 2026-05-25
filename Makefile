# Agent Testbench — root Makefile
# Delegates to module Makefiles / package managers.

.PHONY: build build-cli build-web \
        test test-api test-harness test-cli test-web \
        test-integration smoke \
        coverage coverage-api coverage-harness coverage-cli \
        lint lint-api lint-harness lint-cli \
        clean clean-cli clean-web

# ── Build ─────────────────────────────────────────────────────────────────────

build: build-cli build-web

build-cli:
	$(MAKE) -C cli build

build-web:
	cd web && npm run build

# ── Test ──────────────────────────────────────────────────────────────────────

test: test-api test-harness test-cli test-web

test-api:
	cd api && uv run pytest

test-harness:
	cd harness && uv run pytest

test-cli:
	$(MAKE) -C cli test

test-web:
	cd web && npm run test -- --run

# Run integration tests against a live stack (requires docker compose up)
test-integration:
	docker compose --profile test run --rm tests

# Run curl smoke tests against a live API
smoke:
	bash tests/smoke/smoke.sh

# ── Coverage ──────────────────────────────────────────────────────────────────

coverage: coverage-api coverage-harness coverage-cli

coverage-api:
	cd api && uv run pytest --cov=src --cov-report=html --cov-report=term-missing

coverage-harness:
	cd harness && uv run pytest --cov=src --cov-report=html --cov-report=term-missing

coverage-cli:
	cd cli && go test ./... -coverprofile=coverage.out && go tool cover -func=coverage.out

# ── Lint ──────────────────────────────────────────────────────────────────────

lint: lint-api lint-harness lint-cli

lint-api:
	cd api && uv run ruff check .

lint-harness:
	cd harness && uv run ruff check .

lint-cli:
	$(MAKE) -C cli lint

# ── Clean ─────────────────────────────────────────────────────────────────────

clean: clean-cli clean-web

clean-cli:
	$(MAKE) -C cli clean

clean-web:
	cd web && rm -rf dist
