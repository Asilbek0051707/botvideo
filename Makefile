# AI YouTube Factory — common tasks.
# On Windows without `make`, run the underlying `docker compose ...` commands
# shown in each target (see README / docs/INSTALL.md).

COMPOSE := docker compose
GPU     := docker compose -f docker-compose.yml -f docker-compose.gpu.yml

.PHONY: help init up up-gpu down logs ps build migrate revision shell-backend shell-worker test lint fmt smoke clean

help:
	@echo "Targets:"
	@echo "  init          Copy .env.example -> .env (if missing)"
	@echo "  up            Build & start the full local stack"
	@echo "  up-gpu        Start with the GPU text-to-video worker"
	@echo "  down          Stop and remove containers"
	@echo "  logs          Tail logs for all services"
	@echo "  migrate       Apply DB migrations (alembic upgrade head)"
	@echo "  revision m=.. Autogenerate a migration"
	@echo "  smoke         Submit a test render job via the API"
	@echo "  test/lint/fmt Run pytest / ruff check / ruff format"

init:
	@test -f .env || cp .env.example .env
	@echo ".env ready — edit it to add API keys."

up:
	$(COMPOSE) up --build -d
	@echo "API:    http://localhost:8000/docs"
	@echo "Flower: http://localhost:5555"
	@echo "MinIO:  http://localhost:9001"

up-gpu:
	$(GPU) up --build -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=100

ps:
	$(COMPOSE) ps

build:
	$(COMPOSE) build

migrate:
	$(COMPOSE) exec backend alembic upgrade head

revision:
	$(COMPOSE) exec backend alembic revision --autogenerate -m "$(m)"

shell-backend:
	$(COMPOSE) exec backend bash

shell-worker:
	$(COMPOSE) exec worker bash

smoke:
	curl -s -X POST http://localhost:8000/api/v1/jobs \
	  -H "Content-Type: application/json" \
	  -H "X-API-Key: $${API_KEY:-devkey-change-me}" \
	  -d '{"topic":"3 mind-blowing facts about the deep ocean","style":"documentary","voice":"narrator"}' | python -m json.tool

test:
	$(COMPOSE) exec backend pytest -q

lint:
	ruff check .

fmt:
	ruff format .

clean:
	$(COMPOSE) down -v
