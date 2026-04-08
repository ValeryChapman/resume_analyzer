FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/src" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /src/bot_service

# Устанавливаем uv для управления зависимостями из lock-файла.
RUN pip install --no-cache-dir uv

# Сначала копируем файлы зависимостей для максимального переиспользования кэша слоёв.
COPY src/bot_service/pyproject.toml src/bot_service/uv.lock ./
RUN uv sync --frozen --no-dev

# Копируем исходный код приложения.
COPY src/bot_service /src/bot_service

# Копируем общий код.
COPY src/shared/__init__.py /src/shared/__init__.py
COPY src/shared/application /src/shared/application
COPY src/shared/domain /src/shared/domain
COPY src/shared/infrastructure /src/shared/infrastructure
COPY src/shared/repositories /src/shared/repositories
