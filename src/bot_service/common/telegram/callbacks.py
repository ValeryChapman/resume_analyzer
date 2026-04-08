from enum import StrEnum


class Callbacks(StrEnum):
    START = "start"
    ADD_VACANCY = "start:add_vacancy"
    GET_VACANCIES = "start:add_vacancies"
