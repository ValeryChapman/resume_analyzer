from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.exceptions.resumes import ResumeError, ResumeValidationError
from shared.infrastructure.postgres.models.resume import Resume
from shared.repositories.resumes import (
    create_resume_repository,
    get_resume_by_hh_id_repository,
)


async def create_resume_service(
    postgres_session: AsyncSession, raw_text: str, hh_id: str | None = None
) -> Resume:
    """
    Создает новое резюме после базовой валидации текста.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param raw_text: Исходный текст резюме.
    :param hh_id: Идентификатор резюме на hh.ru.
    :return: Объект Resume.
    """
    normalized_text = raw_text.strip()
    if not normalized_text:
        raise ResumeValidationError("Описание резюме не может быть пустым.")

    resume = await create_resume_repository(
        postgres_session=postgres_session,
        raw_text=normalized_text,
        hh_id=hh_id,
    )
    if resume is None:
        raise ResumeError("Не удалось сохранить резюме")

    return resume


async def get_resume_by_hh_id_service(
    postgres_session: AsyncSession, hh_id: str
) -> Resume | None:
    """
    Получает резюме по идентификатору hh.ru.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param hh_id: Идентификатор резюме на hh.ru.
    :return: Объект Resume или None.
    """
    return await get_resume_by_hh_id_repository(
        postgres_session=postgres_session,
        hh_id=hh_id,
    )


async def create_resume_from_hh_service(
    postgres_session: AsyncSession, hh_id: str, raw_text: str
) -> tuple[Resume, bool]:
    """
    Создает резюме из hh.ru, если его еще нет в базе.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param hh_id: Идентификатор резюме на hh.ru.
    :param raw_text: Исходный текст резюме.
    :return: Кортеж (объект Resume, было_ли_создано).
    """
    existing_resume = await get_resume_by_hh_id_service(
        postgres_session=postgres_session,
        hh_id=hh_id,
    )
    if existing_resume is not None:
        return existing_resume, False

    normalized_text = raw_text.strip()
    if not normalized_text:
        raise ResumeValidationError("Описание резюме не может быть пустым.")

    resume = await create_resume_repository(
        postgres_session=postgres_session,
        raw_text=normalized_text,
        hh_id=hh_id,
    )
    if resume is not None:
        return resume, True

    existing_resume = await get_resume_by_hh_id_service(
        postgres_session=postgres_session,
        hh_id=hh_id,
    )
    if existing_resume is not None:
        return existing_resume, False

    raise ResumeError("Не удалось сохранить резюме из hh.ru")
