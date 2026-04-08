import logging
from typing import Optional

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

logger = logging.getLogger(__name__)

_telegram_bot_client: Optional[Bot] = None


async def init_telegram_bot_client(token: str) -> Bot:
    """
    Инициализирует глобальный клиент Telegram Bot.

    :param token: Токен Telegram бота.
    :return: Экземпляр Bot.
    """
    global _telegram_bot_client
    if _telegram_bot_client is None:
        logger.info("Инициализация клиента Telegram Bot...")
        _telegram_bot_client = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )

    return _telegram_bot_client


async def get_telegram_bot_client() -> Bot:
    """
    Возвращает клиент Telegram Bot.

    :return: Экземпляр Bot.
    """
    if _telegram_bot_client is None:
        raise RuntimeError(
            "Клиент Telegram Bot не инициализирован. "
            "Вызовите init_telegram_bot_client(...) перед использованием."
        )

    return _telegram_bot_client


async def close_telegram_bot_client() -> None:
    """Закрывает глобальный клиент Telegram Bot."""
    global _telegram_bot_client

    if _telegram_bot_client is not None:
        await _telegram_bot_client.session.close()
        _telegram_bot_client = None
        logger.info("Клиент Telegram Bot закрыт.")
