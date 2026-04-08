import logging
from asyncio import current_task
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

logger = logging.getLogger(__name__)

_postgres_async_engine: Optional[AsyncEngine] = None
_postgres_async_session_factory: Optional[async_scoped_session] = None


def init_postgres_engine(url: str, echo: bool = False) -> AsyncEngine:
    """
    Инициализирует глобальный асинхронный движок SQLAlchemy.

    :param url: Ссылка для подключения к Postgres.
    :param echo: Логирование SQL-запросов.
    """
    global _postgres_async_engine

    if _postgres_async_engine is None:
        logger.info("Инициализация асинхронного движка SQLAlchemy...")
        _postgres_async_engine = create_async_engine(url, echo=echo)

    return _postgres_async_engine


def init_postgres_session_factory(url: str, echo: bool = False) -> async_scoped_session:
    """
    Инициализирует глобальную фабрику асинхронных сессий SQLAlchemy.

    :param url: Ссылка для подключения к Postgres.
    :param echo: Логирование SQL-запросов.
    :return: Экземпляр async_scoped_session.
    """
    global _postgres_async_session_factory

    if _postgres_async_session_factory is None:
        logger.info("Инициализация фабрики асинхронных сессий SQLAlchemy...")
        engine: AsyncEngine = init_postgres_engine(url=url, echo=echo)
        _postgres_async_session_factory = async_scoped_session(
            async_sessionmaker(
                engine,
                expire_on_commit=False,
                autoflush=False,
                future=True,
            ),
            scopefunc=current_task,
        )

    return _postgres_async_session_factory


def get_postgres_async_session_factory() -> async_scoped_session:
    """
    Возвращает глобальную фабрику асинхронных сессий.

    :return: Экземпляр async_scoped_session.
    """
    if _postgres_async_session_factory is None:
        raise RuntimeError(
            "Фабрика асинхронных сессий SQLAlchemy не инициализирована. "
            "Вызовите init_postgres_session_factory(...) перед использованием."
        )

    return _postgres_async_session_factory


@asynccontextmanager
async def get_postgres_async_session() -> AsyncGenerator[AsyncSession, Any]:
    """
    Контекстный менеджер для безопасной работы с асинхронной сессией SQLAlchemy.

    Пример использования:
    ---------------------
    async with get_postgres_async_session() as session:
        result = await session.execute(select(User))
        ...
    """
    async_session_factory: async_scoped_session = get_postgres_async_session_factory()
    async_session: AsyncSession = async_session_factory()
    try:
        logger.debug("Асинхронная сессия SQLAlchemy открыта")
        yield async_session
        await async_session.commit()
    except DBAPIError as exc:
        logger.error(f"Транзакция SQLAlchemy была откачена: {exc}", exc_info=True)
        await async_session.rollback()
        raise
    except Exception as exc:
        logger.error(exc, exc_info=True)
        raise
    finally:
        logger.debug("Сессия SQLAlchemy успешно закрыта")
        await async_session.close()
        await async_session_factory.remove()


async def close_postgres_connections() -> None:
    """Закрывает глобальные объекты SQLAlchemy для Postgres."""
    global _postgres_async_engine, _postgres_async_session_factory

    if _postgres_async_session_factory is not None:
        await _postgres_async_session_factory.remove()
        _postgres_async_session_factory = None

    if _postgres_async_engine is not None:
        await _postgres_async_engine.dispose()
        _postgres_async_engine = None
        logger.info("Глобальные подключения SQLAlchemy к Postgres закрыты.")
