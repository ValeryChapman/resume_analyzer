from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.postgres.models.vacancy import (
    Vacancy,
    VacancyProcessingStatus,
)


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
    postgres_session: AsyncSession, vacancy_id: UUID, user_id: UUID | None = None
) -> Vacancy | None:
    """
    Получает вакансию по идентификатору.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :param user_id: Идентификатор пользователя-владельца (опционально).
    :return: Объект Vacancy или None.
    """
    statement = select(Vacancy).where(Vacancy.id == vacancy_id)
    if user_id is not None:
        statement = statement.where(Vacancy.user_id == user_id)

    result: Result = await postgres_session.execute(statement=statement)
    return result.scalar_one_or_none()


async def update_vacancy_processing_status_repository(
    postgres_session: AsyncSession,
    vacancy_id: UUID,
    processing_status: VacancyProcessingStatus,
    processed_data: dict | None = None,
    title: str | None = None,
    summary: str | None = None,
    update_processed_data: bool = False,
) -> Vacancy | None:
    """
    Обновляет статус обработки вакансии.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :param processing_status: Новый статус обработки.
    :param processed_data: Данные после обработки.
    :param title: Извлеченный заголовок вакансии.
    :param summary: Извлеченная краткая сводка вакансии.
    :param update_processed_data: Обновлять ли поле processed_data.
    :return: Обновленная вакансия или None.
    """
    values: dict[str, object] = {"processing_status": processing_status}
    if update_processed_data:
        values["processed_data"] = processed_data
    if title is not None:
        values["title"] = title
    if summary is not None:
        values["summary"] = summary

    statement = (
        update(Vacancy)
        .where(Vacancy.id == vacancy_id)
        .values(**values)
        .returning(Vacancy)
    )
    result: Result = await postgres_session.execute(statement=statement)
    return result.scalar_one_or_none()


async def delete_vacancy_by_id_repository(
    postgres_session: AsyncSession,
    vacancy_id: UUID,
    user_id: UUID,
) -> bool:
    """
    Удаляет вакансию по идентификатору с проверкой владельца.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :param user_id: Идентификатор пользователя-владельца.
    :return: True, если вакансия удалена, иначе False.
    """
    statement = (
        delete(Vacancy)
        .where(Vacancy.id == vacancy_id, Vacancy.user_id == user_id)
        .returning(Vacancy.id)
    )
    result: Result = await postgres_session.execute(statement=statement)
    return result.scalar_one_or_none() is not None
