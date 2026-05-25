DOCKER_COMPOSE_LOCAL_PATH=./infra/docker/docker-compose.local.yml
DOCKER_COMPOSE_PROD_PATH=./infra/docker/docker-compose.prod.yml
UV_PROJECT_ENVIRONMENT=$(CURDIR)/.venv

ENV_FILE=.env

DOCKER_COMPOSE=docker compose -f $(DOCKER_COMPOSE_LOCAL_PATH) --env-file $(ENV_FILE)
DOCKER_COMPOSE_PROD=docker compose -f $(DOCKER_COMPOSE_PROD_PATH) --env-file $(ENV_FILE)

.PHONY: \
	build build-infra build-app prod-build \
	up start start-d down \
	infra-up infra-start infra-start-d infra-down \
	app-up app-start app-start-d app-down \
	prod-up prod-start prod-start-d prod-down \
	migrate-up migrate-down migrate-revision \
	sync-migration sync-bot sync-vacancy-processing

build: build-infra platform-build

build-infra:
	$(DOCKER_COMPOSE) --profile infra build --no-cache

platform-build:
	$(DOCKER_COMPOSE) --profile platform build --no-cache

prod-build:
	$(DOCKER_COMPOSE_PROD) build --no-cache

up: infra-up

start: infra-start

start-d: infra-start-d

down: infra-down

infra-up:
	$(DOCKER_COMPOSE) --profile infra up

infra-start:
	$(DOCKER_COMPOSE) --profile infra up --build

infra-start-d:
	$(DOCKER_COMPOSE) --profile infra up -d --build

infra-down:
	$(DOCKER_COMPOSE) --profile infra down

platform-up:
	$(DOCKER_COMPOSE) --profile platform up

platform-start:
	$(DOCKER_COMPOSE) --profile platform up --build

platform-build:
	$(DOCKER_COMPOSE) --profile platform build --no-cache

platform-start-d:
	$(DOCKER_COMPOSE) --profile platform up -d --build

platform-down:
	$(DOCKER_COMPOSE) --profile platform down

prod-up:
	$(DOCKER_COMPOSE_PROD) up

prod-start:
	$(DOCKER_COMPOSE_PROD) up --build

prod-start-d:
	$(DOCKER_COMPOSE_PROD) up -d --build

prod-down:
	$(DOCKER_COMPOSE_PROD) down

migrate-up:
	PYTHONPATH=src UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv run --project src/migration_service --no-sync alembic -c src/migration_service/alembic.ini upgrade head

migrate-down:
	PYTHONPATH=src UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv run --project src/migration_service --no-sync alembic -c src/migration_service/alembic.ini downgrade -1

migrate-revision:
	PYTHONPATH=src UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv run --project src/migration_service --no-sync alembic -c src/migration_service/alembic.ini revision --autogenerate -m "$(m)"

sync-migration:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv sync --project src/migration_service --inexact

sync-bot:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv sync --project src/bot_service --inexact

sync-vacancy-processing:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv sync --project src/vacancy_processing_service --inexact

sync-resume-processing:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv sync --project src/resume_processing_service --inexact

sync-matching:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv sync --project src/matching_service --inexact

sync-notification:
	UV_PROJECT_ENVIRONMENT=$(UV_PROJECT_ENVIRONMENT) uv sync --project src/notification_service --inexact