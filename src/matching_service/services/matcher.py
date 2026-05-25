import logging
from collections.abc import Mapping

from pydantic import ValidationError
from redis import asyncio as aioredis

from matching_service.services.llm import calculate_match_score_service
from matching_service.settings import settings
from shared.domain.constants.tasks import RedisStreamName
from shared.domain.dto.tasks import (
    MatchFoundNotificationPayloadSchema,
    MatchingTaskSchema,
    NotificationEventType,
    NotificationTaskSchema,
)
from shared.infrastructure.postgres.session import get_postgres_async_session
from shared.services.match_results import upsert_match_result_service
from shared.services.redis_streams import (
    ack_and_delete_message_service,
    add_message_to_stream_service,
    get_message_delivery_count_service,
)
from shared.services.resumes import get_resume_by_id_service
from shared.services.vacancies import get_all_completed_vacancies_service

logger = logging.getLogger(__name__)


async def _process_matching_task(
    redis: aioredis.Redis, message_id: str, message_data: Mapping[str, str]
) -> None:
    """
    Обрабатывает задачу сопоставления резюме со всеми вакансиями.

    :param redis: Асинхронный клиент Redis.
    :param message_id: Идентификатор сообщения в Redis Stream.
    :param message_data: Данные сообщения.
    """
    should_ack = False
    task: MatchingTaskSchema | None = None
    delivery_count = 0
    try:
        task = MatchingTaskSchema.model_validate(message_data)

        delivery_count = await get_message_delivery_count_service(
            redis=redis,
            stream_name=RedisStreamName.MATCHING,
            group_name=settings.matching.consumer_group,
            message_id=message_id,
        )

        if delivery_count > settings.matching.max_delivery_attempts:
            logger.warning(
                f"Сообщение удалено после превышения лимита попыток: "
                f"message_id={message_id} attempts={delivery_count} "
                f"max_attempts={settings.matching.max_delivery_attempts}",
            )
            await ack_and_delete_message_service(
                redis=redis,
                stream_name=RedisStreamName.MATCHING,
                group_name=settings.matching.consumer_group,
                message_id=message_id,
            )
            return

        if not task.resume_id:
            logger.error(f"Задача не содержит resume_id: {message_data}")
            should_ack = True
            return

        logger.info(
            f"Получена задача сопоставления резюме: message_id={message_id} resume_id={task.resume_id}"
        )

        async with get_postgres_async_session() as postgres_session:
            resume = await get_resume_by_id_service(
                postgres_session=postgres_session,
                resume_id=task.resume_id,
            )
            vacancies = await get_all_completed_vacancies_service(
                postgres_session=postgres_session
            )

        if not vacancies:
            logger.info(
                "Нет подходящих вакансий (со статусом completed) для сопоставления."
            )
            should_ack = True
            return

        for vacancy in vacancies:
            try:
                logger.info(
                    f"Сопоставление резюме {resume.id} с вакансией {vacancy.id}"
                )
                match_data = await calculate_match_score_service(
                    vacancy_text=vacancy.raw_text,
                    vacancy_structured=vacancy.processed_data or {},
                    resume_text=resume.raw_text,
                    resume_structured=resume.processed_data or {},
                )

                is_suitable = (
                    match_data.score >= settings.matching.notification_threshold
                )

                async with get_postgres_async_session() as postgres_session:
                    match_result = await upsert_match_result_service(
                        postgres_session=postgres_session,
                        vacancy_id=vacancy.id,
                        resume_id=resume.id,
                        score=match_data.score,
                        is_suitable=is_suitable,
                        reasoning=match_data.reasoning,
                    )

                # Отправляем событие в Notification Service, если кандидат подходит
                if is_suitable:
                    logger.info(
                        f"Кандидат подходит (score={match_data.score}), отправляем уведомление."
                    )
                    notification_task = NotificationTaskSchema(
                        event_type=NotificationEventType.MATCH_FOUND,
                        payload=MatchFoundNotificationPayloadSchema(
                            match_result_id=match_result.id,
                        ),
                    )
                    await add_message_to_stream_service(
                        redis=redis,
                        stream_name=RedisStreamName.NOTIFICATIONS,
                        message_data={
                            "event_type": notification_task.event_type.value,
                            "payload": notification_task.payload.model_dump_json(),
                        },
                    )

            except Exception as exc:
                logger.error(
                    f"Ошибка сопоставления резюме {resume.id} с вакансией {vacancy.id}: {exc}",
                    exc_info=True,
                )

        should_ack = True
    except ValidationError as exc:
        logger.error(
            f"Некорректный формат задачи в Redis Stream: message_id={message_id} error={exc} payload={dict(message_data)}",
            exc_info=True,
        )
        should_ack = True
    except Exception as exc:
        logger.error(
            f"Ошибка обработки задачи резюме: message_id={message_id} error={exc}",
            exc_info=True,
        )
        if (
            task is not None
            and delivery_count >= settings.matching.max_delivery_attempts
        ):
            logger.error(
                "Достигнут лимит попыток обработки резюме, переводим в failed: "
                f"resume_id={task.resume_id} attempts={delivery_count}",
            )
            should_ack = True
    finally:
        if should_ack:
            await ack_and_delete_message_service(
                redis=redis,
                stream_name=RedisStreamName.MATCHING,
                group_name=settings.matching.consumer_group,
                message_id=message_id,
            )
