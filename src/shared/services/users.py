from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from shared.domain.exceptions.users import UserNotFoundError
from shared.infrastructure.postgres.models.user import User
from shared.repositories.users import (
    create_user_repository,
    get_user_by_id_repository,
    get_user_by_telegram_id_repository,
)


async def create_user_service(
    postgres_session: AsyncSession, telegram_id: int
) -> User | None:
    """
    Создает нового пользователя или возвращает существующего.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param telegram_id: Telegram ID пользователя.
    :return: Объект User или None.
    """
    user = await create_user_repository(
        postgres_session=postgres_session, telegram_id=telegram_id
    )
    if not user:
        raise UserNotFoundError(f"Пользователь с Telegram ID {telegram_id} не найден")

    return user


async def get_user_by_id_service(postgres_session: AsyncSession, user_id: UUID) -> User:
    """
    Получает пользователя по идентификатору.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Объект User.
    """
    user = await get_user_by_id_repository(
        postgres_session=postgres_session, user_id=user_id
    )
    if not user:
        raise UserNotFoundError(f"Пользователь с идентификатором {user_id} не найден")

    return user


async def get_user_by_telegram_id_service(
    postgres_session: AsyncSession, telegram_id: int
) -> User | None:
    """
    Получает пользователя по Telegram ID.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param telegram_id: Telegram ID пользователя.
    :return: Объект User.
    """
    user = await get_user_by_telegram_id_repository(
        postgres_session=postgres_session, telegram_id=telegram_id
    )
    if not user:
        raise UserNotFoundError(f"Пользователь с Telegram ID {telegram_id} не найден")

    return user
