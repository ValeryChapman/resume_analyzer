from shared.domain.exceptions.default import DefaultException


class VacancyError(DefaultException):
    message = "Ошибка обработки вакансии"


class VacancyNotFoundError(VacancyError):
    message = "Вакансия не найдена"


class VacancyValidationError(VacancyError):
    message = "Некорректные данные вакансии"
