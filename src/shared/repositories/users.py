from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from shared.infrastructure.postgres.models.user import User


async def create_user_repository(
    postgres_session: AsyncSession, telegram_id: int
) -> User | None:
    """
    Создает нового пользователя или возвращает существующего.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param telegram_id: Telegram ID пользователя.
    :return: Объект User или None.
    """
    statement = (
        insert(User)
        .values(telegram_id=telegram_id)
        .on_conflict_do_update(
            index_elements=[User.telegram_id],
            set_={"telegram_id": telegram_id},
        )
        .returning(User)
    )
    result: Result = await postgres_session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_id_repository(
    postgres_session: AsyncSession, user_id: UUID
) -> User | None:
    """
    Получает пользователя по идентификатору.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param user_id: Идентификатор пользователя.
    :return: Объект User или None.
    """
    statement = select(User).where(User.id == user_id)
    result: Result = await postgres_session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_telegram_id_repository(
    postgres_session: AsyncSession, telegram_id: int
) -> User | None:
    """
    Получает пользователя по Telegram ID.

    :param postgres_session: Асинхронная сессия SQLAlchemy.
    :param telegram_id: Telegram ID пользователя.
    :return: Объект User или None.
    """
    statement = select(User).where(User.telegram_id == telegram_id)
    result: Result = await postgres_session.execute(statement)
    return result.scalar_one_or_none()
