import logging
from typing import Mapping

from pydantic import ValidationError
from redis import asyncio as aioredis

from notification_service.services.events import process_match_found_event
from notification_service.settings import settings
from shared.domain.constants.tasks import RedisStreamName
from shared.domain.dto.tasks import NotificationEventType, NotificationTaskSchema
from shared.services.redis_streams import (
    ack_and_delete_message_service,
    get_message_delivery_count_service,
)

logger = logging.getLogger(__name__)


async def _process_notification_task(
    redis: aioredis.Redis, message_id: str, message_data: Mapping[str, str]
) -> None:
    """
    Обрабатывает одно сообщение из потока уведомлений и подтверждает его.

    :param redis: Асинхронный клиент Redis.
    :param message_id: Идентификатор сообщения в Redis Stream.
    :param message_data: Данные сообщения.
    """
    should_ack = False
    task: NotificationTaskSchema | None = None
    delivery_count = 0
    try:
        task = NotificationTaskSchema.model_validate(message_data)

        delivery_count = await get_message_delivery_count_service(
            redis=redis,
            stream_name=RedisStreamName.NOTIFICATIONS,
            group_name=settings.notification_processing.consumer_group,
            message_id=message_id,
        )

        if delivery_count > settings.notification_processing.max_delivery_attempts:
            logger.warning(
                "Сообщение удалено после превышения лимита попыток: "
                f"message_id={message_id} attempts={delivery_count} "
                f"max_attempts={settings.notification_processing.max_delivery_attempts}",
            )
            await ack_and_delete_message_service(
                redis=redis,
                stream_name=RedisStreamName.NOTIFICATIONS,
                group_name=settings.notification_processing.consumer_group,
                message_id=message_id,
            )
            return

        logger.info(
            f"Получена задача обработки уведомления: message_id={message_id} event_type={task.event_type}"
        )
        match task.event_type:
            case NotificationEventType.MATCH_FOUND:
                await process_match_found_event(
                    match_result_id=task.payload.match_result_id
                )
            case _:
                logger.warning(f"Неизвестный тип события: {task.event_type}")

        should_ack = True
    except ValidationError as exc:
        logger.error(
            f"Некорректный формат задачи в Redis Stream: message_id={message_id} error={exc} payload={dict(message_data)}",
            exc_info=True,
        )
        should_ack = True
    except Exception as exc:
        logger.error(
            f"Ошибка обработки задачи уведомления: message_id={message_id} error={exc}",
            exc_info=True,
        )
        if (
            task is not None
            and delivery_count >= settings.notification_processing.max_delivery_attempts
        ):
            logger.error(
                "Достигнут лимит попыток обработки уведомления, переводим в failed: "
                f"match_result_id={task.payload.match_result_id} attempts={delivery_count}",
            )
            should_ack = True
    finally:
        if should_ack:
            await ack_and_delete_message_service(
                redis=redis,
                stream_name=RedisStreamName.NOTIFICATIONS,
                group_name=settings.notification_processing.consumer_group,
                message_id=message_id,
            )
