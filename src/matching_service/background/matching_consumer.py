import asyncio
import logging

from redis import asyncio as aioredis

from matching_service.services.consumer import start_consumer_service
from shared.infrastructure.redis.client import get_redis_client

logger = logging.getLogger(__name__)


async def run_matching_consumer_background_task() -> None:
    """
    Запускает фоновую задачу Matching Consumer.
    """
    logger.info("Фоновая задача Matching Consumer запущена")

    redis_client: aioredis.Redis = await get_redis_client()

    try:
        await start_consumer_service(redis=redis_client)
    except asyncio.CancelledError:
        logger.info("Фоновая задача Matching Consumer остановлена")
        raise
    except Exception:
        logger.exception("Фоновая задача Matching Consumer завершилась с ошибкой")
        raise
