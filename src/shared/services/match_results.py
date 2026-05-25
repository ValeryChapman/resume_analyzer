from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.exceptions.match_results import (
    MatchResultError,
    MatchResultNotFoundError,
)
from shared.infrastructure.postgres.models.match_result import MatchResult
from shared.repositories.match_results import (
    get_match_result_by_id_repository,
    get_match_results_by_vacancy_id_repository,
    upsert_match_result_repository,
)


async def upsert_match_result_service(
    postgres_session: AsyncSession,
    vacancy_id: UUID,
    resume_id: UUID,
    score: float,
    is_suitable: bool,
    reasoning: str,
) -> MatchResult:
    """
    Создает или обновляет результат сопоставления.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :param resume_id: Идентификатор резюме.
    :param score: Оценка соответствия.
    :param is_suitable: Является ли подходящим.
    :param reasoning: Обоснование оценки.
    :return: Объект MatchResult.
    """
    match_result = await upsert_match_result_repository(
        postgres_session=postgres_session,
        vacancy_id=vacancy_id,
        resume_id=resume_id,
        score=score,
        is_suitable=is_suitable,
        reasoning=reasoning,
    )
    if match_result is None:
        raise MatchResultError("Не удалось сохранить результат совпадения")

    return match_result


async def get_match_result_by_id_service(
    postgres_session: AsyncSession, match_result_id: UUID
) -> MatchResult | None:
    """
    Получает результат сопоставления по идентификатору.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param match_result_id: Идентификатор результата сравнения.
    :return: Объект MatchResult.
    """
    match_result = await get_match_result_by_id_repository(
        postgres_session=postgres_session, match_result_id=match_result_id
    )
    if match_result is None:
        raise MatchResultNotFoundError(
            f"Результат совпадения с идентификатором {match_result_id} не найден"
        )

    return match_result


async def get_match_results_by_vacancy_id_service(
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
    return await get_match_results_by_vacancy_id_repository(
        postgres_session=postgres_session,
        vacancy_id=vacancy_id,
        limit=limit,
        offset=offset,
    )
