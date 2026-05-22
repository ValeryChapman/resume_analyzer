from uuid import UUID

from shared.domain.dto.tasks import (
    ResumeProcessingTaskSchema,
    VacancyProcessingTaskSchema,
)
from shared.repositories.tasks import (
    send_resume_processing_task_repository,
    send_vacancy_processing_task_repository,
)


async def send_vacancy_processing_task_service(vacancy_id: UUID) -> str:
    """
    Отправляет задачу на обработку вакансии в Redis Streams.

    :param vacancy_id: Идентификатор вакансии.
    :return: Идентификатор сообщения в Redis Stream.
    """
    task = VacancyProcessingTaskSchema(vacancy_id=vacancy_id)
    return await send_vacancy_processing_task_repository(task=task)


async def send_resume_processing_task_service(resume_id: UUID) -> str:
    """
    Отправляет задачу на обработку резюме в Redis Streams.

    :param resume_id: Идентификатор резюме.
    :return: Идентификатор сообщения в Redis Stream.
    """
    task = ResumeProcessingTaskSchema(resume_id=resume_id)
    return await send_resume_processing_task_repository(task=task)
