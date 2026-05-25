# Agent Testbench — root Makefile
# Delegates to module Makefiles / package managers.

.PHONY: build build-cli build-web \
        test test-api test-harness test-cli \
        lint lint-api lint-harness lint-cli \
        clean clean-cli clean-web

# ── Build ─────────────────────────────────────────────────────────────────────

build: build-cli build-web

build-cli:
	$(MAKE) -C cli build

build-web:
	cd web && npm run build

# ── Test ──────────────────────────────────────────────────────────────────────

test: test-api test-harness test-cli

test-api:
	cd api && uv run pytest

test-harness:
	cd harness && uv run pytest

test-cli:
	$(MAKE) -C cli test

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
