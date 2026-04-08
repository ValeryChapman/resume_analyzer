from shared.domain.exceptions.default import DefaultException


class UserError(DefaultException):
    message = "General user processing error"


class UserNotFoundError(UserError):
    default_message = "User not found"
