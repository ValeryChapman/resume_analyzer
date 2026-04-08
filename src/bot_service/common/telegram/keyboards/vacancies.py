from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot_service.common.telegram.callbacks import (
    Callbacks,
    VacanciesCallback,
    VacancyCallback,
)
from bot_service.common.telegram.keyboards.pagination import pagination_buttons
from bot_service.common.telegram.texts.buttons import ButtonText
from bot_service.common.telegram.texts.messages.vacancies import vacancy_button_text
from bot_service.common.tools.pagination import get_total_pages
from shared.infrastructure.postgres.models.vacancy import Vacancy


def add_vacancy_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonText.BACK,
                    callback_data=Callbacks.START,
                ),
            ]
        ]
    )


def vacancies_list_pagination_keyboard(
    vacancies: Sequence[Vacancy],
    total_vacancies: int,
    current_page: int,
    page_size: int = 5,
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    for vacancy in vacancies:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=vacancy_button_text(vacancy=vacancy),
                    callback_data=VacancyCallback(id=vacancy.id).pack(),
                )
            ]
        )

    total_pages: int = get_total_pages(total=total_vacancies, page_size=page_size)
    keyboard.inline_keyboard.append(
        pagination_buttons(
            current_page=current_page,
            total_pages=total_pages,
            callback_data=VacanciesCallback,  # noqa
        )
    )
    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text=ButtonText.BACK,
                callback_data=Callbacks.START,
            ),
        ]
    )
    return keyboard


def vacancy_details_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonText.BACK,
                    callback_data=VacanciesCallback(page=1).pack(),
                ),
            ]
        ]
    )
