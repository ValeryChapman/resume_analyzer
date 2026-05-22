import asyncio
import logging
from asyncio import Task

from redis import asyncio as aioredis

from resume_processing_service.services.resumes import _process_resume_task
from resume_processing_service.settings import settings
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
        stream_name=RedisStreamName.RESUME_PROCESSING,
        group_name=settings.resume_processing.consumer_group,
    )

    max_parallel_tasks = settings.resume_processing.max_parallel_tasks
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
                    stream_name=RedisStreamName.RESUME_PROCESSING,
                    group_name=settings.resume_processing.consumer_group,
                    consumer_name=settings.resume_processing.consumer_name,
                    min_idle_time_ms=settings.resume_processing.stale_task_idle_ms,
                    count=min(
                        available_slots,
                        settings.resume_processing.reclaim_batch_size,
                    ),
                )
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error(
                    f"Ошибка claim зависших сообщений Redis Streams: {exc}",
                    exc_info=True,
                )
                await asyncio.sleep(settings.resume_processing.error_sleep_seconds)
                continue

            for message_id, message_data in reclaimed_messages:
                task = asyncio.create_task(
                    _process_resume_task(
                        redis=redis,
                        message_id=message_id,
                        message_data=message_data,
                    ),
                    name=f"resume_processing_reclaimed_{message_id}",
                )
                active_tasks.add(task)

            available_slots -= len(reclaimed_messages)
            if available_slots <= 0:
                continue

            try:
                response = await redis.xreadgroup(
                    groupname=settings.resume_processing.consumer_group,
                    consumername=settings.resume_processing.consumer_name,
                    streams={RedisStreamName.RESUME_PROCESSING: ">"},
                    count=available_slots,
                    block=settings.resume_processing.read_block_ms,
                )
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.error(
                    f"Критическая ошибка в цикле чтения Redis Streams: {exc}",
                    exc_info=True,
                )
                await asyncio.sleep(settings.resume_processing.error_sleep_seconds)
                continue

            if not response:
                continue

            for _, messages in response:
                for message_id, message_data in messages:
                    task = asyncio.create_task(
                        _process_resume_task(
                            redis=redis,
                            message_id=message_id,
                            message_data=message_data,
                        ),
                        name=f"resume_processing_{message_id}",
                    )
                    active_tasks.add(task)
    finally:
        if active_tasks:
            for task in active_tasks:
                task.cancel()
            await asyncio.gather(*active_tasks, return_exceptions=True)
