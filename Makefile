# Agent Testbench — root Makefile
# Delegates to module Makefiles / package managers.

.PHONY: build build-cli build-web \
        test test-api test-harness test-cli test-web \
        test-integration smoke \
        coverage coverage-api coverage-harness coverage-cli \
        lint lint-api lint-harness lint-cli \
        deploy deploy-dev deploy-stage deploy-prod deploy-api deploy-web \
        clean clean-cli clean-web

GIT_SHA     := $(shell git rev-parse --short HEAD)
PROJECT_NAME ?= agent-testbench

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

# ── Deploy ────────────────────────────────────────────────────────────────────
# Generic: make deploy HARBOR_REGISTRY=harbor.taylor.lan/myproject
# Env-specific: make deploy-dev   (reads HARBOR_REGISTRY_DEV_PREFIX from env)
#               make deploy-stage (reads HARBOR_REGISTRY_STAGE_PREFIX from env)
#               make deploy-prod  (reads HARBOR_REGISTRY_PROD_PREFIX from env)

deploy: deploy-api deploy-web

deploy-dev:
	$(MAKE) deploy HARBOR_REGISTRY=$(HARBOR_REGISTRY_DEV_PREFIX)

deploy-stage:
	$(MAKE) deploy HARBOR_REGISTRY=$(HARBOR_REGISTRY_STAGE_PREFIX)

deploy-prod:
	$(MAKE) deploy HARBOR_REGISTRY=$(HARBOR_REGISTRY_PROD_PREFIX)

deploy-api:
ifndef HARBOR_REGISTRY
	$(error HARBOR_REGISTRY is not set — use deploy-dev/deploy-stage/deploy-prod or pass HARBOR_REGISTRY=...)
endif
	docker build -t $(HARBOR_REGISTRY)/$(PROJECT_NAME)-api:$(GIT_SHA) -t $(HARBOR_REGISTRY)/$(PROJECT_NAME)-api:latest ./api
	docker push $(HARBOR_REGISTRY)/$(PROJECT_NAME)-api:$(GIT_SHA)
	docker push $(HARBOR_REGISTRY)/$(PROJECT_NAME)-api:latest

deploy-web:
ifndef HARBOR_REGISTRY
	$(error HARBOR_REGISTRY is not set — use deploy-dev/deploy-stage/deploy-prod or pass HARBOR_REGISTRY=...)
endif
	docker build \
		--build-arg VITE_API_URL=$(VITE_API_URL) \
		-t $(HARBOR_REGISTRY)/$(PROJECT_NAME)-web:$(GIT_SHA) \
		-t $(HARBOR_REGISTRY)/$(PROJECT_NAME)-web:latest \
		./web
	docker push $(HARBOR_REGISTRY)/$(PROJECT_NAME)-web:$(GIT_SHA)
	docker push $(HARBOR_REGISTRY)/$(PROJECT_NAME)-web:latest

# ── Clean ─────────────────────────────────────────────────────────────────────

clean: clean-cli clean-web

clean-cli:
	$(MAKE) -C cli clean

clean-web:
	cd web && rm -rf dist
