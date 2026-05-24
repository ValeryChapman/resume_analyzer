from shared.domain.exceptions.default import DefaultException


class MatchResultError(DefaultException):
    message = "Ошибка обработки результата совпадения"


class MatchResultNotFoundError(MatchResultError):
    message = "Результат совпадения не найден"


class MatchResultValidationError(MatchResultError):
    message = "Некорректные данные результата совпадения"
