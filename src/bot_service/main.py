import asyncio
import logging

from bot_service.background.telegram_bot import run_telegram_bot_background_task
from bot_service.settings import settings
from shared.infrastructure.logging import setup_logging
from shared.infrastructure.postgres.session import init_postgres_session_factory
from shared.infrastructure.redis.client import close_redis_client, init_redis_client
from shared.infrastructure.telegram_bot import (
    close_telegram_bot_client,
    init_telegram_bot_client,
)


async def main() -> None:
    # Глобальная инициализация инфраструктуры процесса.
    setup_logging(level=logging.INFO)

    # Инициализация подключения Postgres
    init_postgres_session_factory(url=settings.postgres.url)

    # Инициализация асинхронного Redis клиента.
    await init_redis_client(url=settings.redis.url)

    # Инициализация Telegram Bot клиента.
    await init_telegram_bot_client(token=settings.telegram_bot.token)

    tasks = [
        asyncio.create_task(
            run_telegram_bot_background_task(),
            name="telegram_bot_worker",
        ),
    ]

    try:
        await asyncio.gather(*tasks)
    finally:
        await close_redis_client()
        await close_telegram_bot_client()


if __name__ == "__main__":
    asyncio.run(main())
