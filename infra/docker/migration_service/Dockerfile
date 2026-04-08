FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/src" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /src/migration_service

# Устанавливаем uv для управления зависимостями из lock-файла.
RUN pip install --no-cache-dir uv

# Сначала копируем файлы зависимостей для максимального переиспользования кэша слоёв.
COPY src/migration_service/pyproject.toml src/migration_service/uv.lock ./
RUN uv sync --frozen --no-dev

# Копируем исходный код приложения.
COPY src/migration_service /src/migration_service

# Копируем общий код.
COPY src/shared/__init__.py /src/shared/__init__.py
COPY src/shared/infrastructure/__init__.py /src/shared/infrastructure/__init__.py
COPY src/shared/infrastructure/postgres /src/shared/infrastructure/postgres
