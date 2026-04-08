from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot_service.common.telegram.callbacks import Callbacks
from bot_service.common.telegram.texts.buttons import ButtonText


def start_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text=ButtonText.ADD_VACANCY, callback_data=Callbacks.ADD_VACANCY
            ),
            InlineKeyboardButton(
                text=ButtonText.GET_VACANCIES, callback_data=Callbacks.GET_VACANCIES
            ),
        ]
    )
    return keyboard
