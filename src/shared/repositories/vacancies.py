from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.postgres.models.vacancy import Vacancy


async def create_vacancy_repository(
    postgres_session: AsyncSession, user_id: UUID, raw_text: str
) -> Vacancy:
    """
    Создает новую вакансию.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :param raw_text: Исходный текст вакансии.
    :return: Объект Vacancy.
    """
    statement = (
        insert(Vacancy).values(user_id=user_id, raw_text=raw_text).returning(Vacancy)
    )
    result: Result = await postgres_session.execute(statement)
    return result.scalar_one_or_none()


async def get_vacancies_by_user_id_repository(
    postgres_session: AsyncSession,
    user_id: UUID,
    limit: int = 10,
    offset: int = 0,
) -> Sequence[Vacancy]:
    """
    Получает список вакансий пользователя с пагинацией.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :param limit: Количество записей.
    :param offset: Смещение для пагинации.
    :return: Список объектов Vacancy.
    """
    statement = (
        select(Vacancy)
        .where(Vacancy.user_id == user_id)
        .order_by(Vacancy.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result: Result = await postgres_session.execute(statement=statement)
    return result.scalars().all()


async def get_vacancies_count_by_user_id_repository(
    postgres_session: AsyncSession, user_id: UUID
) -> int:
    """
    Получает общее количество вакансий пользователя.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Количество вакансий.
    """
    statement = (
        select(func.count()).select_from(Vacancy).where(Vacancy.user_id == user_id)
    )
    result: Result = await postgres_session.execute(statement=statement)
    return int(result.scalar_one())


async def get_vacancy_by_id_repository(
    postgres_session: AsyncSession, vacancy_id: UUID, user_id: UUID
) -> Vacancy | None:
    """
    Получает вакансию по идентификатору с проверкой владельца.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :param user_id: Идентификатор пользователя-владельца.
    :return: Объект Vacancy или None.
    """
    statement = select(Vacancy).where(
        Vacancy.id == vacancy_id,
        Vacancy.user_id == user_id,
    )
    result: Result = await postgres_session.execute(statement=statement)
    return result.scalar_one_or_none()
