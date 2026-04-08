from shared.domain.exceptions.default import DefaultException
from shared.domain.exceptions.users import UserError, UserNotFoundError
from shared.domain.exceptions.vacancies import (
    VacancyError,
    VacancyNotFoundError,
    VacancyValidationError,
)

__all__ = [
    "DefaultException",
    "UserError",
    "UserNotFoundError",
    "VacancyError",
    "VacancyNotFoundError",
    "VacancyValidationError",
]
