FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/src" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /src/notification_service

# Устанавливаем uv для управления зависимостями из lock-файла.
RUN pip install --no-cache-dir uv

# Сначала копируем файлы зависимостей для максимального переиспользования кэша слоёв.
COPY src/notification_service/pyproject.toml src/notification_service/uv.lock* ./
RUN uv sync --frozen --no-dev

# Копируем исходный код приложения.
COPY src/notification_service /src/notification_service

# Копируем общий код.
COPY src/shared/__init__.py /src/shared/__init__.py

## infrastructure
COPY src/shared/infrastructure/__init__.py /src/shared/infrastructure/__init__.py

## infrastructure –> logger
COPY src/shared/infrastructure/logger /src/shared/infrastructure/logger

## infrastructure –> redis
COPY src/shared/infrastructure/redis /src/shared/infrastructure/redis

## infrastructure –> postgres
COPY src/shared/infrastructure/postgres/__init__.py /src/shared/infrastructure/postgres/__init__.py
COPY src/shared/infrastructure/postgres/session.py /src/shared/infrastructure/postgres/session.py

## infrastructure –> postgres –> models
COPY src/shared/infrastructure/postgres/models /src/shared/infrastructure/postgres/models

## infrastructure –> telegram_bot
COPY src/shared/infrastructure/telegram_bot /src/shared/infrastructure/telegram_bot

## services
COPY src/shared/services/__init__.py /src/shared/services/__init__.py
COPY src/shared/services/redis_streams.py /src/shared/services/redis_streams.py
COPY src/shared/services/resumes.py /src/shared/services/resumes.py
COPY src/shared/services/vacancies.py /src/shared/services/vacancies.py
COPY src/shared/services/users.py /src/shared/services/users.py
COPY src/shared/services/match_results.py /src/shared/services/match_results.py

## repositories
COPY src/shared/repositories/__init__.py /src/shared/repositories/__init__.py
COPY src/shared/repositories/resumes.py /src/shared/repositories/resumes.py
COPY src/shared/repositories/vacancies.py /src/shared/repositories/vacancies.py
COPY src/shared/repositories/users.py /src/shared/repositories/users.py
COPY src/shared/repositories/match_results.py /src/shared/repositories/match_results.py

## domain
COPY src/shared/domain/__init__.py /src/shared/domain/__init__.py

## domain –> constants
COPY src/shared/domain/constants/__init__.py /src/shared/domain/constants/__init__.py
COPY src/shared/domain/constants/tasks.py /src/shared/domain/constants/tasks.py

## domain –> dto
COPY src/shared/domain/dto/__init__.py /src/shared/domain/dto/__init__.py
COPY src/shared/domain/dto/tasks.py /src/shared/domain/dto/tasks.py

## domain –> entities
COPY src/shared/domain/entities/__init__.py /src/shared/domain/entities/__init__.py
COPY src/shared/domain/entities/common.py /src/shared/domain/entities/common.py
COPY src/shared/domain/entities/resumes.py /src/shared/domain/entities/resumes.py
COPY src/shared/domain/entities/vacancies.py /src/shared/domain/entities/vacancies.py

## domain –> exceptions
COPY src/shared/domain/exceptions/__init__.py /src/shared/domain/exceptions/__init__.py
COPY src/shared/domain/exceptions/default.py /src/shared/domain/exceptions/default.py
COPY src/shared/domain/exceptions/resumes.py /src/shared/domain/exceptions/resumes.py
COPY src/shared/domain/exceptions/vacancies.py /src/shared/domain/exceptions/vacancies.py
COPY src/shared/domain/exceptions/users.py /src/shared/domain/exceptions/users.py
COPY src/shared/domain/exceptions/match_results.py /src/shared/domain/exceptions/match_results.py
