# Сервис миграций

## Установка зависимостей

Используйте проектный sync без `--active`, чтобы не перезаписывать зависимости других сервисов:

```bash
UV_PROJECT_ENVIRONMENT="$(git rev-parse --show-toplevel)/.venv" uv sync --project src/migration_service --inexact
```

## Команды миграций

Через `Makefile`:

```bash
make migrate-up
make migrate-down
make migrate-revision m="message"
```

Важно:
- Команду нужно выполнять из корня репозитория.
- Если вы уже в `src/migration_service`, используйте `uv sync --inexact` (без `--project src/migration_service`).
