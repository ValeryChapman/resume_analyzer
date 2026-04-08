from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from bot_service.common.telegram.texts.buttons import ButtonText


def back_pagination_button(
    current_page: int, total_pages: int, callback_data: CallbackData
) -> InlineKeyboardButton:
    back_page: int = total_pages if current_page <= 1 else current_page - 1
    return InlineKeyboardButton(
        text=ButtonText.PAGINATION_BACK,
        callback_data=callback_data(page=back_page).pack(),  # noqa
    )


def next_pagination_button(
    current_page: int, total_pages: int, callback_data: CallbackData
) -> InlineKeyboardButton:
    next_page: int = 1 if current_page >= total_pages else current_page + 1
    return InlineKeyboardButton(
        text=ButtonText.PAGINATION_NEXT,
        callback_data=callback_data(page=next_page).pack(),  # noqa
    )


def current_pagination_page_button(
    current_page: int, total_pages: int, callback_data: CallbackData
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=f"{current_page}/{total_pages}",
        callback_data=callback_data(page=current_page).pack(),  # noqa
    )


def pagination_buttons(
    current_page: int, total_pages: int, callback_data: CallbackData
) -> list[InlineKeyboardButton]:
    return [
        back_pagination_button(
            current_page=current_page,
            total_pages=total_pages,
            callback_data=callback_data,
        ),
        current_pagination_page_button(
            current_page=current_page,
            total_pages=total_pages,
            callback_data=callback_data,
        ),
        next_pagination_button(
            current_page=current_page,
            total_pages=total_pages,
            callback_data=callback_data,
        ),
    ]
