import json

from openai import AsyncOpenAI
from pydantic import ValidationError

from shared.domain.entities.vacancies import VacancyStructuredData
from shared.infrastructure.ollama.client import get_ollama_async_client
from vacancy_processing_service.settings import settings

VACANCY_PROCESSING_SYSTEM_PROMPT = """
Преобразуй текст вакансии в JSON по заданной схеме.

Верни только JSON.
Не добавляй пояснения.
Не выдумывай данные.

Правила извлечения:
- title — название должности из текста.
- seniority — junior, middle, senior или unknown.
- experience — минимальное количество лет опыта числом, если оно указано явно, иначе null.
- skills — все явно указанные технологии, инструменты и языки программирования.
- education:
  - higher, если явно указано высшее образование;
  - secondary, если явно указано среднее образование;
  - unknown, если образование не указано.
- short_summary — одно короткое предложение на русском.

Нормализация:
- Postgres -> PostgreSQL
- JS -> JavaScript
- Py -> Python

Если поле отсутствует:
- null для одиночного неизвестного значения,
- [] для списков,
- "unknown" для enum.
""".strip()


def _response_json_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "title": {
                "type": ["string", "null"],
                "description": "Название должности, например Python разработчик.",
            },
            "seniority": {
                "type": "string",
                "enum": ["junior", "middle", "senior", "unknown"],
                "description": "Уровень позиции.",
            },
            "experience": {
                "type": ["integer", "null"],
                "description": "Минимальный опыт работы в годах, если указан явно.",
            },
            "skills": {
                "type": "array",
                "description": "Список явно указанных технологий и навыков.",
                "items": {
                    "type": "string",
                    "description": "Один навык или технология.",
                },
            },
            "education": {
                "type": "string",
                "enum": ["secondary", "higher", "unknown"],
                "description": "Требуемый уровень образования.",
            },
            "short_summary": {
                "type": "string",
                "description": "Краткое описание вакансии одним предложением на русском.",
            },
        },
        "required": [
            "title",
            "seniority",
            "experience",
            "skills",
            "education",
            "short_summary",
        ],
    }


async def structure_vacancy_text_service(raw_text: str) -> VacancyStructuredData:
    """
    Преобразует текст вакансии в структурированный формат с помощью языковой модели.

    :param raw_text: Исходный текст вакансии.
    :return: Структурированная вакансия.
    :raises ValueError: Если ответ модели пустой или невалидный.
    """
    ollama_client: AsyncOpenAI = get_ollama_async_client()
    schema = _response_json_schema()

    response = await ollama_client.chat.completions.create(
        model=settings.ollama.llm_name,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": VACANCY_PROCESSING_SYSTEM_PROMPT,
            },
            {"role": "user", "content": raw_text},
        ],
        extra_body={"format": schema},
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
