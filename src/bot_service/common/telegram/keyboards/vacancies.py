from collections.abc import Sequence
from uuid import UUID

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot_service.common.telegram.callbacks import (
    Callbacks,
    VacanciesCallback,
    VacancyCallback,
    VacancyDeleteCallback,
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


def vacancy_details_keyboard(vacancy_id: UUID) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonText.DELETE_VACANCY,
                    callback_data=VacancyDeleteCallback(id=vacancy_id).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text=ButtonText.BACK,
                    callback_data=VacanciesCallback(page=1).pack(),
                ),
            ],
        ]
    )


def vacancy_deleted_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=ButtonText.START,
                    callback_data=Callbacks.START,
                ),
            ]
        ]
    )
