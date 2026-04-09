import asyncio
import logging

from shared.infrastructure.logger.setup import setup_logging
from shared.infrastructure.ollama.client import init_ollama_async_client
from shared.infrastructure.postgres.session import init_postgres_session_factory
from shared.infrastructure.redis.client import close_redis_client, init_redis_client
from vacancy_processing_service.background import (
    run_vacancy_processing_consumer_background_task,
)
from vacancy_processing_service.settings import settings


async def main() -> None:
    # Глобальная инициализация инфраструктуры процесса.
    setup_logging(level=logging.INFO)

    # Инициализация подключения Postgres.
    init_postgres_session_factory(url=settings.postgres.url)

    # Инициализация асинхронного Redis клиента.
    await init_redis_client(url=settings.redis.url)

    # Инициализация асинхронного Ollama клиента.
    init_ollama_async_client(
        base_url=settings.ollama.base_url,
        api_key=settings.ollama.api_key,
        timeout=settings.ollama.timeout,
    )

    tasks = [
        asyncio.create_task(
            run_vacancy_processing_consumer_background_task(),
            name="vacancy_processing_consumer_worker",
        )
    ]

    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await close_redis_client()


if __name__ == "__main__":
    asyncio.run(main())
