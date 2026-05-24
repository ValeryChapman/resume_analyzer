from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.exceptions.resumes import (
    ResumeError,
    ResumeNotFoundError,
    ResumeValidationError,
)
from shared.infrastructure.postgres.models.resume import Resume, ResumeProcessingStatus
from shared.repositories.resumes import (
    create_resume_repository,
    get_resume_by_hh_id_repository,
    get_resume_by_id_repository,
    update_resume_processing_status_repository,
)


async def create_resume_service(
    postgres_session: AsyncSession, hh_id: str, raw_text: str
) -> Resume:
    """
    Создает новое резюме после базовой валидации текста.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param raw_text: Исходный текст резюме.
    :param hh_id: Идентификатор резюме на HeadHunter.
    :return: Объект Resume.
    """
    normalized_text = raw_text.strip()
    if not normalized_text:
        raise ResumeValidationError("Описание резюме не может быть пустым.")

    resume = await create_resume_repository(
        postgres_session=postgres_session, raw_text=normalized_text, hh_id=hh_id
    )
    if resume is None:
        raise ResumeError("Не удалось сохранить резюме")

    return resume


async def get_resume_by_id_service(
    postgres_session: AsyncSession, resume_id: UUID
) -> Resume:
    """
    Получает резюме по идентификатору для внутренней обработки сервисами.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param resume_id: Идентификатор резюме.
    :return: Объект Resume.
    """
    resume = await get_resume_by_id_repository(
        postgres_session=postgres_session, resume_id=resume_id
    )
    if resume is None:
        raise ResumeNotFoundError(f"Резюме с идентификатором {resume_id} не найдено")

    return resume


async def get_resume_by_hh_id_service(
    postgres_session: AsyncSession, hh_id: str
) -> Resume:
    """
    Получает резюме по идентификатору HeadHunter.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param hh_id: Идентификатор резюме на HeadHunter.
    :return: Объект Resume или None.
    """
    resume = await get_resume_by_hh_id_repository(
        postgres_session=postgres_session, hh_id=hh_id
    )
    if resume is None:
        raise ResumeNotFoundError(
            f"Резюме с идентификатором HeadHunter {hh_id} не найдено"
        )

    return resume


async def update_resume_processing_status_service(
    postgres_session: AsyncSession,
    resume_id: UUID,
    processing_status: ResumeProcessingStatus,
    processed_data: dict | None = None,
    title: str | None = None,
    summary: str | None = None,
    update_processed_data: bool = False,
) -> Resume:
    """
    Обновляет статус обработки резюме.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param resume_id: Идентификатор резюме.
    :param processing_status: Новый статус обработки резюме.
    :param processed_data: Данные после обработки.
    :param title: Извлеченный заголовок резюме.
    :param summary: Извлеченная краткая сводка резюме.
    :param update_processed_data: Обновлять ли поле processed_data.
    :return: Обновленное резюме.
    """
    resume = await update_resume_processing_status_repository(
        postgres_session=postgres_session,
        resume_id=resume_id,
        processing_status=processing_status,
        processed_data=processed_data,
        title=title,
        summary=summary,
        update_processed_data=update_processed_data,
    )
    if resume is None:
        raise ResumeNotFoundError(f"Резюме с идентификатором {resume_id} не найдено")

    return resume
