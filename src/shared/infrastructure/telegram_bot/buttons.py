from enum import StrEnum


class ButtonText(StrEnum):
    BACK = "Назад"
    START = "Главное меню"

    ADD_VACANCY = "Добавить вакансию"
    DELETE_VACANCY = "🗑 Удалить вакансию"
    GET_VACANCIES = "📄 Мои вакансии"
    GET_MATCHES = "🤝 Кандидаты"
    OPEN_VACANCY = "📄 Открыть вакансию"
    PAGINATION_BACK = "<––"
    PAGINATION_NEXT = "––>"
