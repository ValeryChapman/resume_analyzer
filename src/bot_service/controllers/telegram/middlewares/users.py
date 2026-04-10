from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from shared.services.users import create_user_service


class EnsureTelegramUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        postgres_session = data.get("postgres_session")

        telegram_id = getattr(data.get("event_from_user"), "id", None)
        if not isinstance(telegram_id, int):
            data["db_user"] = None
            return await handler(event, data)

        current_user = await create_user_service(
            postgres_session=postgres_session,
            telegram_id=telegram_id,
        )

        data["db_user"] = current_user
        return await handler(event, data)
