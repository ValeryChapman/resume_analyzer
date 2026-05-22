from shared.domain.exceptions.default import DefaultException


class ResumeError(DefaultException):
    message = "Ошибка обработки резюме"


class ResumeNotFoundError(ResumeError):
    message = "Резюме не найдено"


class ResumeValidationError(ResumeError):
    message = "Некорректные данные резюме"
