from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.postgres.models.resume import Resume


async def create_resume_repository(
    postgres_session: AsyncSession,
    raw_text: str,
    hh_id: str | None = None,
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
