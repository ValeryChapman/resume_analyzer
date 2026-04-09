import logging
from collections.abc import Mapping
from typing import Any

from redis import asyncio as aioredis
from redis.exceptions import ResponseError

logger = logging.getLogger(__name__)


async def create_consumer_group_service(
    redis: aioredis.Redis,
    stream_name: str,
    group_name: str,
    from_id: str = "0",
    mkstream: bool = True,
) -> None:
    """
    Универсально создает группу потребителей Redis Streams, если она еще не существует.

    :param redis: Асинхронный клиент Redis.
    :param stream_name: Имя Redis Stream.
    :param group_name: Имя consumer group.
    :param from_id: ID, с которого группа начнет чтение.
    :param mkstream: Создавать stream, если он отсутствует.
    """
    try:
        await redis.xgroup_create(
            name=stream_name,
            groupname=group_name,
            id=from_id,
            mkstream=mkstream,
        )
        logger.info(
            f"Группа потребителей '{group_name}' для потока '{stream_name}' успешно создана"
        )
    except ResponseError as exc:
        if "BUSYGROUP" in str(exc):
            logger.info(
                f"Группа потребителей '{group_name}' для потока '{stream_name}' уже существует"
            )
            return

        logger.error(
            f"Ошибка при создании группы потребителей '{group_name}' для потока '{stream_name}': {exc}",
            exc_info=True,
        )
        raise


async def ack_and_delete_message_service(
    redis: aioredis.Redis, stream_name: str, group_name: str, message_id: str
) -> None:
    """
    Подтверждает обработку сообщения и его из Redis Stream.

    :param redis: Асинхронный клиент Redis.
    :param stream_name: Имя Redis Stream.
    :param group_name: Имя consumer group.
    :param message_id: Идентификатор сообщения.
    """
    await redis.xack(stream_name, group_name, message_id)
    await redis.xdel(stream_name, message_id)


async def get_message_delivery_count_service(
    redis: aioredis.Redis,
    stream_name: str,
    group_name: str,
    message_id: str,
) -> int:
    """
    Возвращает число доставок сообщения в рамках consumer group.

    :param redis: Асинхронный клиент Redis.
    :param stream_name: Имя Redis Stream.
    :param group_name: Имя consumer group.
    :param message_id: Идентификатор сообщения.
    :return: Число доставок сообщения.
    """
    pending = await redis.xpending_range(
        name=stream_name,
        groupname=group_name,
        min=message_id,
        max=message_id,
        count=1,
    )
    if not pending:
        return 0

    entry = pending[0]
    if isinstance(entry, dict):
        return int(entry.get("times_delivered", 0))

    if isinstance(entry, (list, tuple)) and len(entry) >= 4:
        return int(entry[3])

    return 0


def _extract_xautoclaim_messages(response: Any) -> list[tuple[str, Mapping[str, str]]]:
    """
    Нормализует ответ xautoclaim от redis-py в список сообщений.

    :param response: Ответ redis клиента.
    :return: Список сообщений (message_id, message_data).
    """
    if not response or not isinstance(response, (list, tuple)):
        return []

    if len(response) >= 2 and isinstance(response[1], list):
        return response[1]

    return []


async def claim_stale_messages_service(
    redis: aioredis.Redis,
    stream_name: str,
    group_name: str,
    consumer_name: str,
    min_idle_time_ms: int,
    count: int,
    start_id: str = "0-0",
) -> list[tuple[str, Mapping[str, str]]]:
    """
    Переназначает зависшие сообщения текущему consumer'у через XAUTOCLAIM.

    :param redis: Асинхронный клиент Redis.
    :param stream_name: Имя Redis Stream.
    :param group_name: Имя consumer group.
    :param consumer_name: Имя consumer.
    :param min_idle_time_ms: Минимальный idle таймаут сообщения для reclaim.
    :param count: Максимальное количество сообщений.
    :param start_id: Стартовый ID для XAUTOCLAIM.
    :return: Список сообщений (message_id, message_data).
    """
    if count <= 0:
        return []

    response = await redis.xautoclaim(
        name=stream_name,
        groupname=group_name,
        consumername=consumer_name,
        min_idle_time=min_idle_time_ms,
        start_id=start_id,
        count=count,
    )
    return _extract_xautoclaim_messages(response)
