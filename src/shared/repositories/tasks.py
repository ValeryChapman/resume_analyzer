from shared.domain.constants.tasks import RedisStreamName
from shared.domain.dto.tasks import (
    ResumeProcessingTaskSchema,
    VacancyProcessingTaskSchema,
)
from shared.infrastructure.redis.client import get_redis_client


async def send_vacancy_processing_task_repository(
    task: VacancyProcessingTaskSchema,
) -> str:
    """
    Публикует задачу обработки вакансии в Redis Stream.

    :param task: Схема задачи обработки вакансии.
    :return: Идентификатор сообщения в потоке.
    """
    redis_client = await get_redis_client()
    message_id = await redis_client.xadd(
        name=RedisStreamName.VACANCY_PROCESSING, fields=task.model_dump(mode="json")
    )
    return str(message_id)


async def send_resume_processing_task_repository(
    task: ResumeProcessingTaskSchema,
) -> str:
    """
    Публикует задачу обработки резюме в Redis Stream.

    :param task: Схема задачи обработки резюме.
    :return: Идентификатор сообщения в потоке.
    """
    redis_client = await get_redis_client()
    message_id = await redis_client.xadd(
        name=RedisStreamName.RESUME_PROCESSING, fields=task.model_dump(mode="json")
    )
    return str(message_id)
