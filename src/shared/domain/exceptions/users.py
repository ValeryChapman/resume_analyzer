from shared.domain.exceptions.default import DefaultException


class UserError(DefaultException):
    message = "Ошибка обработки пользователя"


class UserNotFoundError(UserError):
    default_message = "Пользователь не найден"
