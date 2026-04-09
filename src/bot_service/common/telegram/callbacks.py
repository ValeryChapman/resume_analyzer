from enum import StrEnum
from uuid import UUID

from aiogram.filters.callback_data import CallbackData


class Callbacks(StrEnum):
    START = "start"
    ADD_VACANCY = "start:add_vacancy"
    GET_VACANCIES = "start:get_vacancies"


class VacanciesCallback(CallbackData, prefix="vacancies_page"):
    page: int


class VacancyCallback(CallbackData, prefix="vacancy"):
    id: UUID


class VacancyDeleteCallback(CallbackData, prefix="vacancy_delete"):
    id: UUID
