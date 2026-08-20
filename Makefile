.PHONY: help install install-backend install-frontend env \
	dev backend frontend verify lint check-openai build

ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
BACKEND := $(ROOT)/backend
FRONTEND := $(ROOT)/frontend

# Prefer a real pnpm on PATH; otherwise use the packageManager pin via npx.
PNPM_VERSION := 11.3.0
PNPM := $(shell command -v pnpm 2>/dev/null || echo "npx --yes pnpm@$(PNPM_VERSION)")

help:
	@echo "Invoice Review — common targets"
	@echo ""
	@echo "  make install          Install backend + frontend deps (locked)"
	@echo "  make env              Create .env files from examples if missing"
	@echo "  make dev              Run API (8000) + Vite UI together"
	@echo "  make backend          Run FastAPI only on :8000"
	@echo "  make frontend         Run Vite only"
	@echo "  make verify           Lint backend, typecheck/lint/build frontend"
	@echo "  make check-openai     Probe live OpenAI credentials"
	@echo "  make lint             Backend ruff + frontend eslint/tsc"
	@echo "  make build            Frontend production build"
	@echo ""
	@echo "First-time: make install && make env  # then edit backend/.env"
	@echo "Daily:      make dev"
	@echo "pnpm:       $(PNPM)"

install: install-backend install-frontend

install-backend:
	cd "$(BACKEND)" && uv sync --locked

install-frontend:
	cd "$(FRONTEND)" && $(PNPM) install --frozen-lockfile

env:
	@if [ ! -f "$(BACKEND)/.env" ]; then \
		cp "$(BACKEND)/.env.example" "$(BACKEND)/.env"; \
		echo "Created backend/.env — set OPENAI_API_KEY"; \
	else \
		echo "backend/.env already exists"; \
	fi
	@if [ ! -f "$(FRONTEND)/.env" ]; then \
		cp "$(FRONTEND)/.env.example" "$(FRONTEND)/.env"; \
		echo "Created frontend/.env"; \
	else \
		echo "frontend/.env already exists"; \
	fi

dev:
	"$(ROOT)/scripts/dev.sh"

backend:
	cd "$(BACKEND)" && uv run --locked --no-sync \
		uvicorn app.main:create_app --factory --reload --port 8000

frontend:
	cd "$(FRONTEND)" && $(PNPM) dev

lint:
	cd "$(BACKEND)" && uv run --locked --no-sync ruff check app scripts
	cd "$(FRONTEND)" && $(PNPM) exec tsc -b --pretty false
	cd "$(FRONTEND)" && $(PNPM) lint

check-openai:
	cd "$(BACKEND)" && uv run --locked --no-sync python scripts/check_openai.py

build:
	cd "$(FRONTEND)" && $(PNPM) build

verify: lint check-openai build
