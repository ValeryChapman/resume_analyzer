from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.exceptions.vacancies import (
    VacancyError,
    VacancyNotFoundError,
    VacancyValidationError,
)
from shared.infrastructure.postgres.models.vacancy import (
    Vacancy,
    VacancyProcessingStatus,
)
from shared.repositories.vacancies import (
    create_vacancy_repository,
    delete_vacancy_by_id_repository,
    get_vacancies_by_user_id_repository,
    get_vacancies_count_by_user_id_repository,
    get_vacancy_by_id_repository,
    update_vacancy_processing_status_repository,
)

MIN_VACANCY_TEXT_LENGTH = 100
MAX_VACANCY_TEXT_LENGTH = 3000
MAX_PAGINATION_LIMIT = 100


async def create_vacancy_service(
    postgres_session: AsyncSession, user_id: UUID, raw_text: str
) -> Vacancy:
    """
    Создает новую вакансию после базовой валидации текста.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :param raw_text: Исходный текст вакансии.
    :return: Объект Vacancy.
    """
    normalized_text = raw_text.strip()
    if len(normalized_text) < MIN_VACANCY_TEXT_LENGTH:
        raise VacancyValidationError(
            f"Описание вакансии должно быть не короче {MIN_VACANCY_TEXT_LENGTH} символов."
        )
    if len(normalized_text) > MAX_VACANCY_TEXT_LENGTH:
        raise VacancyValidationError(
            f"Описание вакансии должно быть не длиннее {MAX_VACANCY_TEXT_LENGTH} символов."
        )

    vacancy = await create_vacancy_repository(
        postgres_session=postgres_session, user_id=user_id, raw_text=normalized_text
    )
    if vacancy is None:
        raise VacancyError("Не удалось сохранить вакансию")

    return vacancy


async def get_vacancies_by_user_id_service(
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
    if limit <= 0 or limit > MAX_PAGINATION_LIMIT:
        raise VacancyValidationError(
            f"Параметр limit должен быть в диапазоне 1..{MAX_PAGINATION_LIMIT}."
        )
    if offset < 0:
        raise VacancyValidationError("Параметр offset не может быть отрицательным.")

    return await get_vacancies_by_user_id_repository(
        postgres_session=postgres_session,
        user_id=user_id,
        limit=limit,
        offset=offset,
    )


async def get_vacancies_count_by_user_id_service(
    postgres_session: AsyncSession, user_id: UUID
) -> int:
    """
    Получает общее количество вакансий пользователя.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Количество вакансий.
    """
    return await get_vacancies_count_by_user_id_repository(
        postgres_session=postgres_session, user_id=user_id
    )


async def get_vacancy_by_id_service(
    postgres_session: AsyncSession,
    vacancy_id: UUID,
    user_id: UUID,
) -> Vacancy:
    """
    Получает вакансию по идентификатору.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :param user_id: Идентификатор пользователя-владельца.
    :return: Объект Vacancy.
    """
    vacancy = await get_vacancy_by_id_repository(
        postgres_session=postgres_session,
        vacancy_id=vacancy_id,
        user_id=user_id,
    )
    if vacancy is None:
        raise VacancyNotFoundError(
            f"Вакансия с идентификатором {vacancy_id} не найдена"
        )

    return vacancy


async def get_vacancy_by_id_for_processing_service(
    postgres_session: AsyncSession,
    vacancy_id: UUID,
) -> Vacancy:
    """
    Получает вакансию по идентификатору для внутренней обработки сервисами.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :return: Объект Vacancy.
    """
    vacancy = await get_vacancy_by_id_repository(
        postgres_session=postgres_session,
        vacancy_id=vacancy_id,
    )
    if vacancy is None:
        raise VacancyNotFoundError(
            f"Вакансия с идентификатором {vacancy_id} не найдена"
        )

    return vacancy


async def update_vacancy_processing_status_service(
    postgres_session: AsyncSession,
    vacancy_id: UUID,
    processing_status: VacancyProcessingStatus,
    processed_data: dict | None = None,
    update_processed_data: bool = False,
) -> Vacancy:
    """
    Обновляет статус обработки вакансии.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :param processing_status: Новый статус обработки вакансии.
    :param processed_data: Данные после обработки.
    :param update_processed_data: Обновлять ли поле processed_data.
    :return: Обновленная вакансия.
    """
    vacancy = await update_vacancy_processing_status_repository(
        postgres_session=postgres_session,
        vacancy_id=vacancy_id,
        processing_status=processing_status,
        processed_data=processed_data,
        update_processed_data=update_processed_data,
    )
    if vacancy is None:
        raise VacancyNotFoundError(
            f"Вакансия с идентификатором {vacancy_id} не найдена"
        )

    return vacancy


async def delete_vacancy_by_id_service(
    postgres_session: AsyncSession,
    vacancy_id: UUID,
    user_id: UUID,
) -> None:
    """
    Удаляет вакансию по идентификатору с проверкой владельца.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param vacancy_id: Идентификатор вакансии.
    :param user_id: Идентификатор пользователя-владельца.
    :raises VacancyNotFoundError: Если вакансия не найдена.
    """
    is_deleted = await delete_vacancy_by_id_repository(
        postgres_session=postgres_session,
        vacancy_id=vacancy_id,
        user_id=user_id,
    )
    if not is_deleted:
        raise VacancyNotFoundError(
            f"Вакансия с идентификатором {vacancy_id} не найдена"
        )
