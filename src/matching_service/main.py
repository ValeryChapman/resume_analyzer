import asyncio
import logging

from matching_service.background import run_matching_consumer_background_task
from matching_service.settings import settings
from shared.infrastructure.llm.client import init_llm_async_client
from shared.infrastructure.logger.setup import setup_logging
from shared.infrastructure.postgres.session import init_postgres_session_factory
from shared.infrastructure.redis.client import close_redis_client, init_redis_client


async def main() -> None:
    # Глобальная инициализация инфраструктуры процесса.
    setup_logging(level=logging.INFO)

    # Инициализация подключения Postgres.
    init_postgres_session_factory(url=settings.postgres.url)

    # Инициализация асинхронного Redis клиента.
    await init_redis_client(url=settings.redis.url)

    # Инициализация асинхронного Ollama клиента.
    init_llm_async_client(
        base_url=settings.llm.base_url,
        api_key=settings.llm.api_key,
        timeout=settings.llm.timeout,
    )

    tasks = [
        asyncio.create_task(
            run_matching_consumer_background_task(),
            name="matching_consumer_worker",
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
