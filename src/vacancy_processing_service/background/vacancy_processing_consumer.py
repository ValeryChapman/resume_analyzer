import asyncio
import logging

from redis import asyncio as aioredis

from shared.infrastructure.redis.client import get_redis_client
from vacancy_processing_service.services.consumer import start_consumer_service

logger = logging.getLogger(__name__)


async def run_vacancy_processing_consumer_background_task() -> None:
    """
    Запускает фоновую задачу Vacancy Processing Consumer.
    """
    logger.info("Фоновая задача Vacancy Processing Consumer запущена")

    redis_client: aioredis.Redis = await get_redis_client()

    try:
        await start_consumer_service(redis=redis_client)
    except asyncio.CancelledError:
        logger.info("Фоновая задача Vacancy Processing Consumer остановлена")
        raise
    except Exception:
        logger.exception(
            "Фоновая задача Vacancy Processing Consumer завершилась с ошибкой"
        )
        raise
    finally:
        ...
