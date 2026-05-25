from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from shared.infrastructure.telegram_bot.buttons import ButtonText
from shared.infrastructure.telegram_bot.callbacks import Callbacks, VacancyCallback


def match_found_keyboard(vacancy_id: UUID) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для уведомления о найденном соответствии.

    :param vacancy_id: Идентификатор вакансии.
    :return: Объект InlineKeyboardMarkup.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonText.OPEN_VACANCY,
                    callback_data=VacancyCallback(id=vacancy_id).pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=ButtonText.START,
                    callback_data=Callbacks.START,
                )
            ],
        ]
    )
