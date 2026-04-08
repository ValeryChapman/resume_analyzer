import logging
from typing import Optional

from redis import asyncio as aioredis

logger = logging.getLogger(__name__)

_redis_async_client: Optional[aioredis.Redis] = None


async def init_redis_client(url: str) -> aioredis.Redis:
    """
    Инициализирует глобальный асинхронный клиент Redis.

    :param url: Ссылка для подключения к Redis.
    :return: Экземпляр aioredis.Redis.
    """
    global _redis_async_client
    if _redis_async_client is None:
        logger.info("Инициализация асинхронного клиента Redis...")
        _redis_async_client = aioredis.from_url(
            url,
            encoding="utf-8",
            decode_responses=True,
        )
        await _redis_async_client.ping()

    return _redis_async_client


async def get_redis_client() -> aioredis.Redis:
    """
    Возвращает асинхронный клиент Redis.

    :return: Экземпляр aioredis.Redis.
    """
    if _redis_async_client is None:
        raise RuntimeError(
            "Клиент Redis не инициализирован. "
            "Вызовите init_redis_client(...) перед использованием."
        )

    return _redis_async_client


async def close_redis_client() -> None:
    """Закрывает глобальный асинхронный клиент Redis."""
    global _redis_async_client

    if _redis_async_client is not None:
        if hasattr(_redis_async_client, "aclose"):
            await _redis_async_client.aclose()
        else:
            await _redis_async_client.close()
        _redis_async_client = None
        logger.info("Асинхронный клиент Redis закрыт.")
