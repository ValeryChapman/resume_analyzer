import logging
from collections.abc import Mapping

from pydantic import ValidationError
from redis import asyncio as aioredis

from resume_processing_service.services.llm import structure_resume_text_service
from resume_processing_service.settings import settings
from shared.domain.constants.tasks import RedisStreamName
from shared.domain.dto.tasks import MatchingTaskSchema, ResumeProcessingTaskSchema
from shared.domain.entities.resumes import ResumeStructuredData
from shared.domain.exceptions.resumes import ResumeNotFoundError
from shared.infrastructure.postgres.models.resume import ResumeProcessingStatus
from shared.infrastructure.postgres.session import get_postgres_async_session
from shared.services.redis_streams import (
    ack_and_delete_message_service,
    add_message_to_stream_service,
    get_message_delivery_count_service,
)
from shared.services.resumes import (
    get_resume_by_id_service,
    update_resume_processing_status_service,
)

logger = logging.getLogger(__name__)


async def _process_resume_task(
    redis: aioredis.Redis, message_id: str, message_data: Mapping[str, str]
) -> None:
    """
    Обрабатывает одно сообщение из потока резюме и подтверждает его.

    :param redis: Асинхронный клиент Redis.
    :param message_id: Идентификатор сообщения в Redis Stream.
    :param message_data: Данные сообщения.
    """
    should_ack = False
    task: ResumeProcessingTaskSchema | None = None
    delivery_count = 0
    try:
        task = ResumeProcessingTaskSchema.model_validate(message_data)

        delivery_count = await get_message_delivery_count_service(
            redis=redis,
            stream_name=RedisStreamName.RESUME_PROCESSING,
            group_name=settings.resume_processing.consumer_group,
            message_id=message_id,
        )

        if delivery_count > settings.resume_processing.max_delivery_attempts:
            logger.warning(
                "Сообщение удалено после превышения лимита попыток: "
                f"message_id={message_id} attempts={delivery_count} "
                f"max_attempts={settings.resume_processing.max_delivery_attempts}",
            )
            async with get_postgres_async_session() as postgres_session:
                await update_resume_processing_status_service(
                    postgres_session=postgres_session,
                    resume_id=task.resume_id,
                    processing_status=ResumeProcessingStatus.failed,
                )
            await ack_and_delete_message_service(
                redis=redis,
                stream_name=RedisStreamName.RESUME_PROCESSING,
                group_name=settings.resume_processing.consumer_group,
                message_id=message_id,
            )
            return

        logger.info(
            f"Получена задача обработки резюме: message_id={message_id} resume_id={task.resume_id}"
        )

        async with get_postgres_async_session() as postgres_session:
            resume = await get_resume_by_id_service(
                postgres_session=postgres_session,
                resume_id=task.resume_id,
            )
            await update_resume_processing_status_service(
                postgres_session=postgres_session,
                resume_id=task.resume_id,
                processing_status=ResumeProcessingStatus.processing,
            )

        structured_resume_data: ResumeStructuredData = (
            await structure_resume_text_service(raw_text=resume.raw_text)
        )

        async with get_postgres_async_session() as postgres_session:
            await update_resume_processing_status_service(
                postgres_session=postgres_session,
                resume_id=task.resume_id,
                processing_status=ResumeProcessingStatus.completed,
                processed_data=structured_resume_data.model_dump(mode="json"),
                title=structured_resume_data.title,
                summary=structured_resume_data.summary,
                update_processed_data=True,
            )

        # Отправляем событие в Matching Service
        matching_task = MatchingTaskSchema(resume_id=task.resume_id)
        await add_message_to_stream_service(
            redis=redis,
            stream_name=RedisStreamName.MATCHING,
            message_data=matching_task.model_dump(mode="json"),
        )

        should_ack = True
    except ValidationError as exc:
        logger.error(
            f"Некорректный формат задачи в Redis Stream: message_id={message_id} error={exc} payload={dict(message_data)}",
            exc_info=True,
        )
        should_ack = True
    except ResumeNotFoundError as exc:
        logger.error(
            f"Резюме для обработки не найдено: message_id={message_id} error={exc}",
            exc_info=True,
        )
        if delivery_count >= settings.resume_processing.max_delivery_attempts:
            logger.error(
                "Резюме не найдено после максимального числа попыток, удаляем задачу: "
                f"message_id={message_id} attempts={delivery_count}",
            )
            should_ack = True
    except Exception as exc:
        logger.error(
            f"Ошибка обработки задачи резюме: message_id={message_id} error={exc}",
            exc_info=True,
        )
        if (
            task is not None
            and delivery_count >= settings.resume_processing.max_delivery_attempts
        ):
            logger.error(
                "Достигнут лимит попыток обработки резюме, переводим в failed: "
                f"resume_id={task.resume_id} attempts={delivery_count}",
            )
            async with get_postgres_async_session() as postgres_session:
                await update_resume_processing_status_service(
                    postgres_session=postgres_session,
                    resume_id=task.resume_id,
                    processing_status=ResumeProcessingStatus.failed,
                )
            should_ack = True
    finally:
        if should_ack:
            await ack_and_delete_message_service(
                redis=redis,
                stream_name=RedisStreamName.RESUME_PROCESSING,
                group_name=settings.resume_processing.consumer_group,
                message_id=message_id,
            )
