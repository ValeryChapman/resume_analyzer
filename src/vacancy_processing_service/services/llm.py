import json
from functools import cache

from openai import AsyncOpenAI
from pydantic import ValidationError

from shared.domain.entities.vacancies import VacancyStructuredData
from shared.infrastructure.llm.client import get_llm_async_client
from vacancy_processing_service.settings import settings

VACANCY_PROCESSING_SYSTEM_PROMPT = """
Вы – экспертная аналитическая система по обработке HR-данных. Ваша задача – глубоко проанализировать неструктурированный текст вакансии и экстрагировать ключевые сущности, строго соблюдая предоставленную JSON-схему.

Основные принципы извлечения:
1. Точность и достоверность: Извлекайте только ту информацию, которая явно указана в тексте. Категорически запрещено выдумывать данные, делать допущения или логические выводы за автора вакансии.
2. Компетенции и навыки (skills): Выделите все ключевые профессиональные требования. Это могут быть хард-скиллы, владение специфическим оборудованием или ПО, методологии, знание языков, а также критически важные софт-скиллы.
3. Краткая сводка (short_summary): Сформулируйте суть и главную задачу позиции в одном емком, профессиональном предложении на русском языке.
4. Нормализация данных: Приводите профессиональные термины, аббревиатуры и названия инструментов к общепринятому отраслевому стандарту (например, исправление опечаток в названиях программ, приведение сокращений к единому виду).

Требования к формату ответа:
- Сгенерируйте исключительно валидный JSON-объект, который СТРОГО СООТВЕТСТВУЕТ переданной ниже JSON-схеме.
- Все поля из списка "required" в схеме ОБЯЗАТЕЛЬНЫ к заполнению.
- Запрещено использовать markdown-форматирование (включая блоки ```json).
- Запрещено добавлять любые вводные слова, пояснения или комментарии до и после JSON.
""".strip()


@cache
def _build_system_prompt() -> str:
    """
    Собирает системный промпт со встроенной JSON-схемой ответа.

    :return: Готовый системный промпт.
    """
    schema = VacancyStructuredData.model_json_schema()
    schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
    return f"{VACANCY_PROCESSING_SYSTEM_PROMPT}\n\nОЖИДАЕМАЯ JSON-СХЕМА:\n{schema_str}"


def _build_user_prompt(raw_text: str) -> str:
    """
    Формирует пользовательский промпт с текстом вакансии.

    :param raw_text: Исходный текст вакансии.
    :return: Готовый пользовательский промпт.
    """
    return f"ТЕКСТ ВАКАНСИИ:\n{raw_text}"


async def structure_vacancy_text_service(raw_text: str) -> VacancyStructuredData:
    """
    Преобразует текст вакансии в структурированный формат с помощью языковой модели.

    :param raw_text: Исходный текст вакансии.
    :return: Структурированная вакансия.
    """
    llm_client: AsyncOpenAI = get_llm_async_client()

    response = await llm_client.chat.completions.create(
        model=settings.llm.name,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": _build_system_prompt(),
            },
            {"role": "user", "content": _build_user_prompt(raw_text=raw_text)},
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content if response.choices else None
    if content is None or not content.strip():
        raise ValueError("Пустой ответ от языковой модели.")

    try:
        parsed_data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("Ответ модели не содержит валидный JSON.") from exc

    try:
        return VacancyStructuredData.model_validate(parsed_data)
    except ValidationError as exc:
        raise ValueError(f"Невалидный структурированный ответ модели: {exc}") from exc
