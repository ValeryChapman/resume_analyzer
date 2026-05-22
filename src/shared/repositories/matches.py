from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.postgres.models.match_result import MatchResult


async def upsert_match_result_repository(
    postgres_session: AsyncSession,
    vacancy_id: UUID,
    resume_id: UUID,
    score: float,
    reasoning: str,
) -> MatchResult:
    """
    Создает или обновляет результат сопоставления.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :param resume_id: Идентификатор резюме.
    :param score: Оценка соответствия.
    :param reasoning: Обоснование оценки.
    :return: Объект MatchResult.
    """
    statement = (
        insert(MatchResult)
        .values(
            vacancy_id=vacancy_id,
            resume_id=resume_id,
            score=score,
            reasoning=reasoning,
        )
        .on_conflict_do_update(
            index_elements=["vacancy_id", "resume_id"],
            set_={
                "score": score,
                "reasoning": reasoning,
                "updated_at": select(func.now()).scalar_subquery(),
            },
        )
        .returning(MatchResult)
    )
    result: Result = await postgres_session.execute(statement)
    return result.scalar_one()
