from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from shared.infrastructure.postgres.models.match_result import MatchResult
from shared.infrastructure.postgres.models.vacancy import Vacancy


async def upsert_match_result_repository(
    postgres_session: AsyncSession,
    vacancy_id: UUID,
    resume_id: UUID,
    score: float,
    is_suitable: bool,
    reasoning: str,
) -> MatchResult | None:
    """
    Создает или обновляет результат сопоставления.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :param resume_id: Идентификатор резюме.
    :param score: Оценка соответствия.
    :param is_suitable: Является ли подходящим.
    :param reasoning: Обоснование оценки.
    :return: Объект MatchResult или None.
    """
    statement = (
        insert(MatchResult)
        .values(
            vacancy_id=vacancy_id,
            resume_id=resume_id,
            score=score,
            is_suitable=is_suitable,
            reasoning=reasoning,
        )
        .on_conflict_do_update(
            index_elements=["vacancy_id", "resume_id"],
            set_={
                "score": score,
                "is_suitable": is_suitable,
                "reasoning": reasoning,
                "updated_at": select(func.now()).scalar_subquery(),
            },
        )
        .returning(MatchResult)
    )
    result: Result = await postgres_session.execute(statement)
    return result.scalar_one_or_none()


async def get_match_result_by_id_repository(
    postgres_session: AsyncSession, match_result_id: UUID
) -> MatchResult | None:
    """
    Получает результат сопоставления по идентификатору.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param match_result_id: Идентификатор результата сравнения.
    :return: Объект MatchResult или None.
    """
    statement = (
        select(MatchResult)
        .where(
            MatchResult.id == match_result_id,
        )
        .options(
            joinedload(MatchResult.resume),
            joinedload(MatchResult.vacancy).joinedload(Vacancy.user),
        )
    )
    result: Result = await postgres_session.execute(statement=statement)
    return result.scalar_one_or_none()


async def get_match_results_by_vacancy_id_repository(
    postgres_session: AsyncSession,
    vacancy_id: UUID,
    limit: int = 10,
    offset: int = 0,
) -> tuple[list[MatchResult], int]:
    """
    Получает список результатов сопоставления для вакансии с пагинацией.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :param limit: Количество элементов.
    :param offset: Смещение.
    :return: Кортеж (список результатов, общее количество).
    """
    # Получаем общее количество
    count_statement = select(func.count(MatchResult.id)).where(
        MatchResult.vacancy_id == vacancy_id, MatchResult.is_suitable == True
    )
    total_count: int = (await postgres_session.execute(count_statement)).scalar() or 0

    # Получаем элементы
    statement = (
        select(MatchResult)
        .where(MatchResult.vacancy_id == vacancy_id, MatchResult.is_suitable == True)
        .options(joinedload(MatchResult.resume))
        .order_by(MatchResult.score.desc())
        .limit(limit)
        .offset(offset)
    )

    result: Result = await postgres_session.execute(statement)
    return list(result.scalars().all()), total_count
