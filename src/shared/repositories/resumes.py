from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.postgres.models.resume import Resume, ResumeProcessingStatus


async def create_resume_repository(
    postgres_session: AsyncSession, raw_text: str, hh_id: str | None = None
) -> Resume | None:
    """
    Создает новое резюме.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param raw_text: Исходный текст резюме.
    :param hh_id: Идентификатор резюме на hh.ru.
    :return: Объект Resume или None при конфликте уникальности.
    """
    statement = (
        insert(Resume)
        .values(
            hh_id=hh_id,
            raw_text=raw_text,
        )
        .on_conflict_do_nothing(index_elements=[Resume.hh_id])
        .returning(Resume)
    )
    result: Result = await postgres_session.execute(statement)
    return result.scalar_one_or_none()


async def get_resume_by_hh_id_repository(
    postgres_session: AsyncSession, hh_id: str
) -> Resume | None:
    """
    Получает резюме по идентификатору hh.ru.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param hh_id: Идентификатор резюме на hh.ru.
    :return: Объект Resume или None.
    """
    statement = select(Resume).where(Resume.hh_id == hh_id)
    result: Result = await postgres_session.execute(statement=statement)
    return result.scalar_one_or_none()


async def get_resume_by_id_repository(
    postgres_session: AsyncSession, resume_id: UUID
) -> Resume | None:
    """
    Получает резюме по идентификатору.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param resume_id: Идентификатор резюме.
    :return: Объект Resume или None.
    """
    statement = select(Resume).where(Resume.id == resume_id)
    result: Result = await postgres_session.execute(statement=statement)
    return result.scalar_one_or_none()


async def update_resume_processing_status_repository(
    postgres_session: AsyncSession,
    resume_id: UUID,
    processing_status: ResumeProcessingStatus,
    processed_data: dict | None = None,
    title: str | None = None,
    summary: str | None = None,
    update_processed_data: bool = False,
) -> Resume | None:
    """
    Обновляет статус обработки резюме.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param resume_id: Идентификатор резюме.
    :param processing_status: Новый статус обработки.
    :param processed_data: Данные после обработки.
    :param title: Извлеченный заголовок резюме.
    :param summary: Извлеченная краткая сводка резюме.
    :param update_processed_data: Обновлять ли поле processed_data.
    :return: Обновленное резюме или None.
    """
    values: dict[str, object] = {"processing_status": processing_status}
    if update_processed_data:
        values["processed_data"] = processed_data
    if title is not None:
        values["title"] = title
    if summary is not None:
        values["summary"] = summary

    statement = (
        update(Resume).where(Resume.id == resume_id).values(**values).returning(Resume)
    )
    result: Result = await postgres_session.execute(statement=statement)
    return result.scalar_one_or_none()
