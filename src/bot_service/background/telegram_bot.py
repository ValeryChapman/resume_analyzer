import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from redis import asyncio as aioredis

from bot_service.controllers.telegram import telegram_router
from bot_service.controllers.telegram.middlewares.database import (
    DatabaseSessionMiddleware,
)
from bot_service.controllers.telegram.middlewares.users import (
    EnsureTelegramUserMiddleware,
)
from shared.infrastructure.redis.client import get_redis_client
from shared.infrastructure.telegram_bot import (
    get_telegram_bot_client,
)

logger = logging.getLogger(__name__)


async def _build_fsm_storage() -> BaseStorage:
    try:
        redis_client: aioredis.Redis = await get_redis_client()
        return RedisStorage(redis=redis_client)
    except Exception as exc:
        logger.warning(
            "Redis недоступен для FSM-хранилища, используем in-memory storage: %s",
            exc,
            exc_info=True,
        )
        return MemoryStorage()


async def run_telegram_bot_background_task() -> None:
    """
    Запускает фоновую задачу Telegram Bot.
    """
    logger.info("Фоновая задача Telegram Bot запущена")

    fsm_storage = await _build_fsm_storage()
    dispatcher = Dispatcher(storage=fsm_storage)
    dispatcher.update.outer_middleware(DatabaseSessionMiddleware())
    dispatcher.update.outer_middleware(EnsureTelegramUserMiddleware())
    dispatcher.include_router(telegram_router)

    bot: Bot = await get_telegram_bot_client()

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(
            bot,
            allowed_updates=dispatcher.resolve_used_update_types(),
        )
    except asyncio.CancelledError:
        logger.info("Фоновая задача Telegram Bot остановлена")
        raise
    except Exception:
        logger.exception("Фоновая задача Telegram Bot завершилась с ошибкой")
        raise
    finally:
        await fsm_storage.close()
