import asyncio
import logging
from asyncio import Task

from redis import asyncio as aioredis

from matching_service.services.matcher import _process_matching_task
from matching_service.settings import settings
from shared.domain.constants.tasks import RedisStreamName
from shared.services.redis_streams import (
    claim_stale_messages_service,
    create_consumer_group_service,
)

logger = logging.getLogger(__name__)


async def start_consumer_service(redis: aioredis.Redis) -> None:
    """
    Основной цикл consumer'а Redis Streams с ограничением параллелизма.

    :param redis: Асинхронный клиент Redis.
    """
    await create_consumer_group_service(
        redis=redis,
        stream_name=RedisStreamName.MATCHING,
        group_name=settings.matching.consumer_group,
    )

    max_parallel_tasks = settings.matching.max_parallel_tasks
    active_tasks: set[Task[None]] = set()
    try:
        while True:
            active_tasks = {task for task in active_tasks if not task.done()}
            available_slots = max_parallel_tasks - len(active_tasks)

            if available_slots <= 0:
                await asyncio.wait(active_tasks, return_when=asyncio.FIRST_COMPLETED)
                continue

            try:
                reclaimed_messages = await claim_stale_messages_service(
                    redis=redis,
                    stream_name=RedisStreamName.MATCHING,
                    group_name=settings.matching.consumer_group,
                    consumer_name=settings.matching.consumer_name,
                    min_idle_time_ms=settings.matching.stale_task_idle_ms,
                    count=min(
                        available_slots,
                        settings.matching.reclaim_batch_size,
                    ),
                )
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error(f"Ошибка claim зависших сообщений: {exc}", exc_info=True)
                await asyncio.sleep(settings.matching.error_sleep_seconds)
                continue

            for message_id, message_data in reclaimed_messages:
                task = asyncio.create_task(
                    _process_matching_task(
                        redis=redis,
                        message_id=message_id,
                        message_data=message_data,
                    ),
                    name=f"matching_reclaimed_{message_id}",
                )
                active_tasks.add(task)

            available_slots -= len(reclaimed_messages)
            if available_slots <= 0:
                continue

            try:
                response = await redis.xreadgroup(
                    groupname=settings.matching.consumer_group,
                    consumername=settings.matching.consumer_name,
                    streams={RedisStreamName.MATCHING: ">"},
                    count=available_slots,
                    block=settings.matching.read_block_ms,
                )
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error(
                    f"Ошибка в цикле чтения Redis Streams: {exc}", exc_info=True
                )
                await asyncio.sleep(settings.matching.error_sleep_seconds)
                continue

            if not response:
                continue

            for _, messages in response:
                for message_id, message_data in messages:
                    task = asyncio.create_task(
                        _process_matching_task(
                            redis=redis,
                            message_id=message_id,
                            message_data=message_data,
                        ),
                        name=f"matching_{message_id}",
                    )
                    active_tasks.add(task)
    finally:
        if active_tasks:
            for task in active_tasks:
                task.cancel()
            await asyncio.gather(*active_tasks, return_exceptions=True)
