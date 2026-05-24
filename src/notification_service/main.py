import asyncio
import logging

from notification_service.background import run_notification_consumer_background_task
from notification_service.settings import settings
from shared.infrastructure.logger.setup import setup_logging
from shared.infrastructure.postgres.session import init_postgres_session_factory
from shared.infrastructure.redis.client import close_redis_client, init_redis_client
from shared.infrastructure.telegram_bot.client import (
    close_telegram_bot_client,
    init_telegram_bot_client,
)


async def main() -> None:
    # Глобальная инициализация инфраструктуры процесса.
    setup_logging(level=logging.INFO)

    # Инициализация подключения Postgres.
    init_postgres_session_factory(url=settings.postgres.url)

    # Инициализация асинхронного Redis клиента.
    await init_redis_client(url=settings.redis.url)

    # Инициализация Telegram Bot клиента.
    await init_telegram_bot_client(token=settings.telegram_bot.token)

    tasks = [
        asyncio.create_task(
            run_notification_consumer_background_task(),
            name="notification_consumer_worker",
        )
    ]

    try:
        await asyncio.gather(*tasks)
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await close_telegram_bot_client()
        await close_redis_client()


if __name__ == "__main__":
    asyncio.run(main())
