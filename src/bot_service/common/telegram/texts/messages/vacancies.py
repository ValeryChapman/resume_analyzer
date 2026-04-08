from html import escape

from bot_service.common.tools.dates import format_datetime_moscow
from shared.infrastructure.postgres.models.vacancy import Vacancy


def add_vacancy_prompt_message() -> str:
    return (
        "📄 <b>Добавление вакансии</b>\n\n"
        "Отправьте одним сообщением текст вакансии в свободной форме.\n"
        "Например: требования к стеку, опыт, обязанности, формат работы."
    )


def add_vacancy_validation_message(message: str) -> str:
    return f"Не удалось сохранить вакансию: <i>{escape(message)}</i>"


def add_vacancy_non_text_message() -> str:
    return "Пожалуйста, отправьте текстовое описание вакансии."


def vacancy_not_found_message() -> str:
    return "Вакансия не найдена"


def vacancies_not_found_message() -> str:
    return "У вас пока нет вакансий"


def vacancy_created_message() -> str:
    return "✅ <b>Вакансия добавлена</b>\n\nОписание сохранено и передано в обработку."


def vacancies_list_message() -> str:
    return (
        "📄 <b>Список вакансий</b>\n\n"
        "Ниже представлены ваши вакансии.\n"
        "Выберите нужную, чтобы посмотреть детали или продолжить работу."
    )


def vacancies_empty_message() -> str:
    return "📄 <b>Список вакансий</b>\n\nУ вас пока нет добавленных вакансий."


def vacancy_button_text(vacancy: Vacancy) -> str:
    return _truncate_text(" ".join(vacancy.raw_text.split()), max_length=38)


def _truncate_text(text: str, max_length: int) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[: max_length - 1]}…"


def vacancy_details_message(vacancy: Vacancy) -> str:
    return (
        "📄 <b>Вакансия</b>\n\n"
        f"Статус обработки: <b>{vacancy.processing_status.value}</b>\n"
        f"Создана: <b>{format_datetime_moscow(vacancy.created_at)}</b>\n\n"
        "<b>Описание:</b>\n"
        f"<blockquote>{escape(vacancy.raw_text)}</blockquote>"
    )
