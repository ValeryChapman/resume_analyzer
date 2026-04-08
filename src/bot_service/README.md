# Bot Service

## Установка зависимостей

Используйте проектный sync без `--active`, чтобы не перезаписывать зависимости других сервисов:

```bash
UV_PROJECT_ENVIRONMENT="$(git rev-parse --show-toplevel)/.venv" uv sync --project src/bot_service --inexact
```

## Локальный запуск

```bash
PYTHONPATH=src UV_PROJECT_ENVIRONMENT="$(git rev-parse --show-toplevel)/.venv" uv run --project src/bot_service --no-sync python -m bot_service.main
```

## Через Makefile

```bash
make sync-bot
```

Важно:
- Команду нужно выполнять из корня репозитория.
- Если вы уже в `src/bot_service`, используйте `uv sync --inexact` (без `--project src/bot_service`).
