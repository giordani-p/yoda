.PHONY: help setup install up down restart logs ps build clean \
	db dev-backend dev-frontend test lint format migrate migration \
	generate-client contract-check

BACKEND := cd apps/backend &&
FRONTEND := cd apps/frontend &&

help:
	@echo "Available commands:"
	@echo ""
	@echo "Setup"
	@echo "  make setup            - Create local environment file"
	@echo "  make install          - Install backend and frontend dependencies"
	@echo ""
	@echo "Docker (full stack)"
	@echo "  make up               - Start all services"
	@echo "  make down             - Stop all services"
	@echo "  make restart          - Restart all services"
	@echo "  make logs             - Follow service logs"
	@echo "  make ps               - List running services"
	@echo "  make build            - Build containers"
	@echo "  make clean            - Remove containers and volumes"
	@echo ""
	@echo "Local development"
	@echo "  make db               - Start only the database"
	@echo "  make dev-backend      - Run backend with reload"
	@echo "  make dev-frontend     - Run frontend with reload"
	@echo "  make migrate          - Apply database migrations"
	@echo "  make migration name=x - Create a migration from model changes"
	@echo ""
	@echo "Quality"
	@echo "  make test             - Run all tests"
	@echo "  make lint             - Run all linters and type checks"
	@echo "  make format           - Format all code"
	@echo ""
	@echo "API contract"
	@echo "  make generate-client  - Regenerate frontend types from the contract"
	@echo "  make contract-check   - Check backend and frontend against the contract"

setup:
	@test -f .env || cp .env.example .env
	@echo "Environment file ready."

install:
	$(BACKEND) uv sync
	$(FRONTEND) pnpm install

up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

ps:
	docker compose ps

build:
	docker compose build

clean:
	docker compose down -v --remove-orphans

db:
	docker compose up -d db

dev-backend:
	$(BACKEND) uv run uvicorn app.main:app --reload

dev-frontend:
	$(FRONTEND) pnpm dev

migrate:
	$(BACKEND) uv run alembic upgrade head

migration:
	@test -n "$(name)" || (echo "Usage: make migration name=describe_change" && exit 1)
	$(BACKEND) uv run alembic revision --autogenerate -m "$(name)"

test:
	$(BACKEND) uv run pytest
	$(FRONTEND) pnpm test

lint:
	$(BACKEND) uv run ruff check . && uv run ruff format --check . && uv run lint-imports
	$(FRONTEND) pnpm lint && pnpm format:check && pnpm typecheck

format:
	$(BACKEND) uv run ruff check --fix . && uv run ruff format .
	$(FRONTEND) pnpm format

generate-client:
	$(FRONTEND) pnpm generate

contract-check: generate-client
	$(BACKEND) uv run pytest tests/test_contract.py
	git diff --exit-code apps/frontend/src/services/api/generated
