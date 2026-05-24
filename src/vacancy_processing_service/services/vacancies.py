import logging
from collections.abc import Mapping

from pydantic import ValidationError
from redis import asyncio as aioredis

from shared.domain.constants.tasks import RedisStreamName
from shared.domain.dto.tasks import VacancyProcessingTaskSchema
from shared.domain.entities.vacancies import VacancyStructuredData
from shared.domain.exceptions.vacancies import VacancyNotFoundError
from shared.infrastructure.postgres.models.vacancy import VacancyProcessingStatus
from shared.infrastructure.postgres.session import get_postgres_async_session
from shared.services.redis_streams import (
    ack_and_delete_message_service,
    get_message_delivery_count_service,
)
from shared.services.vacancies import (
    get_vacancy_by_id_service,
    update_vacancy_processing_status_service,
)
from vacancy_processing_service.services.llm import structure_vacancy_text_service
from vacancy_processing_service.settings import settings

logger = logging.getLogger(__name__)


async def _process_vacancy_task(
    redis: aioredis.Redis, message_id: str, message_data: Mapping[str, str]
) -> None:
    """
    Обрабатывает одно сообщение из потока вакансий и подтверждает его.

    :param redis: Асинхронный клиент Redis.
    :param message_id: Идентификатор сообщения в Redis Stream.
    :param message_data: Данные сообщения.
    """
    should_ack = False
    task: VacancyProcessingTaskSchema | None = None
    delivery_count = 0
    try:
        task = VacancyProcessingTaskSchema.model_validate(message_data)

        delivery_count = await get_message_delivery_count_service(
            redis=redis,
            stream_name=RedisStreamName.VACANCY_PROCESSING,
            group_name=settings.vacancy_processing.consumer_group,
            message_id=message_id,
        )

        if delivery_count > settings.vacancy_processing.max_delivery_attempts:
            logger.warning(
                "Сообщение удалено после превышения лимита попыток: "
                f"message_id={message_id} attempts={delivery_count} "
                f"max_attempts={settings.vacancy_processing.max_delivery_attempts}",
            )
            async with get_postgres_async_session() as postgres_session:
                await update_vacancy_processing_status_service(
                    postgres_session=postgres_session,
                    vacancy_id=task.vacancy_id,
                    processing_status=VacancyProcessingStatus.failed,
                )
            await ack_and_delete_message_service(
                redis=redis,
                stream_name=RedisStreamName.VACANCY_PROCESSING,
                group_name=settings.vacancy_processing.consumer_group,
                message_id=message_id,
            )
            return

        logger.info(
            f"Получена задача обработки вакансии: message_id={message_id} vacancy_id={task.vacancy_id}"
        )

        async with get_postgres_async_session() as postgres_session:
            vacancy = await get_vacancy_by_id_service(
                postgres_session=postgres_session,
                vacancy_id=task.vacancy_id,
            )
            await update_vacancy_processing_status_service(
                postgres_session=postgres_session,
                vacancy_id=task.vacancy_id,
                processing_status=VacancyProcessingStatus.processing,
            )

        structured_vacancy_data: VacancyStructuredData = (
            await structure_vacancy_text_service(raw_text=vacancy.raw_text)
        )

        async with get_postgres_async_session() as postgres_session:
            await update_vacancy_processing_status_service(
                postgres_session=postgres_session,
                vacancy_id=task.vacancy_id,
                processing_status=VacancyProcessingStatus.completed,
                processed_data=structured_vacancy_data.model_dump(mode="json"),
                title=structured_vacancy_data.title,
                summary=structured_vacancy_data.summary,
                update_processed_data=True,
            )

        should_ack = True
    except ValidationError as exc:
        logger.error(
            f"Некорректный формат задачи в Redis Stream: message_id={message_id} error={exc} payload={dict(message_data)}",
            exc_info=True,
        )
        # Плохие сообщения подтверждаем, чтобы не блокировать поток.
        should_ack = True
    except VacancyNotFoundError as exc:
        logger.error(
            f"Вакансия для обработки не найдена: message_id={message_id} error={exc}",
            exc_info=True,
        )
        if delivery_count >= settings.vacancy_processing.max_delivery_attempts:
            logger.error(
                "Вакансия не найдена после максимального числа попыток, удаляем задачу: "
                f"message_id={message_id} attempts={delivery_count}",
            )
            should_ack = True
    except Exception as exc:
        logger.error(
            f"Ошибка обработки задачи вакансии: message_id={message_id} error={exc}",
            exc_info=True,
        )
        if (
            task is not None
            and delivery_count >= settings.vacancy_processing.max_delivery_attempts
        ):
            logger.error(
                "Достигнут лимит попыток обработки вакансии, переводим в failed: "
                f"vacancy_id={task.vacancy_id} attempts={delivery_count}",
            )
            async with get_postgres_async_session() as postgres_session:
                await update_vacancy_processing_status_service(
                    postgres_session=postgres_session,
                    vacancy_id=task.vacancy_id,
                    processing_status=VacancyProcessingStatus.failed,
                )
            should_ack = True
    finally:
        if should_ack:
            await ack_and_delete_message_service(
                redis=redis,
                stream_name=RedisStreamName.VACANCY_PROCESSING,
                group_name=settings.vacancy_processing.consumer_group,
                message_id=message_id,
            )
