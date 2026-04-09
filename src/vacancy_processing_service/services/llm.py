import json
from json import JSONDecodeError

from openai import AsyncOpenAI

from shared.domain.entities.vacancies import VacancyStructuredData
from shared.infrastructure.ollama.client import get_ollama_async_client
from vacancy_processing_service.settings import settings

VACANCY_PROCESSING_SYSTEM_PROMPT = """
Ты — сервис структурирования вакансий.

Твоя задача:
преобразовать текст вакансии, написанный в свободной форме, в строго валидный JSON.

Правила:
1. Верни только JSON.
2. Не добавляй markdown, пояснения, комментарии и лишний текст.
3. Не выдумывай факты, которых нет в вакансии.
4. Если данные не указаны, используй:
   - null для одиночных неизвестных значений,
   - [] для списков,
   - "unknown" для enum-полей.
5. Разделяй навыки на обязательные и желательные:
   - если требование явно обязательное, помещай в required_skills;
   - если навык скорее желательный или не указан как обязательный явно, помещай в preferred_skills.
6. Нормализуй названия технологий:
   - Postgres -> PostgreSQL
   - JS -> JavaScript
   - Py -> Python
7. Определи seniority только если это можно разумно вывести из текста:
   - junior
   - middle
   - senior
   - unknown
8. Если в вакансии указан опыт, заполни experience.min_years_total числом.
9. Если указано обязательное высшее образование, заполни:
   - education.required = true
   - education.level = "higher"
10. Сформируй short_summary на русском языке в 1 предложении.
11. Поле raw_text должно содержать исходный текст вакансии без изменений.

Строгая схема JSON:
{
  "title": "string | null",
  "seniority": "junior | middle | senior | unknown",
  "experience": {
    "min_years_total": "number | null"
  },
  "required_skills": [
    {
      "name": "string",
      "importance": "required | preferred"
    }
  ],
  "preferred_skills": [
    {
      "name": "string",
      "importance": "required | preferred"
    }
  ],
  "education": {
    "required": "boolean",
    "level": "higher | unknown"
  },
  "short_summary": "string",
  "raw_text": "string"
}
""".strip()


def _cleanup_json_response(content: str) -> str:
    """
    Очищает ответ модели до JSON-строки.

    :param content: Исходный ответ модели.
    :return: Строка, содержащая JSON.
    """
    cleaned = content.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    return cleaned


def _parse_json_object(content: str) -> dict:
    """
    Парсит JSON-объект из ответа модели.

    :param content: Текст ответа модели.
    :return: Словарь с JSON-данными.
    :raises ValueError: Если не удалось распарсить JSON.
    """
    cleaned = _cleanup_json_response(content=content)

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            parsed = json.loads(cleaned[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except JSONDecodeError as exc:
            raise ValueError("Ответ модели не содержит валидный JSON-объект.") from exc

    raise ValueError("Ответ модели не содержит валидный JSON-объект.")


async def structure_vacancy_text_service(raw_text: str) -> VacancyStructuredData:
    """
    Преобразует текст вакансии в структурированный формат с помощью языковой модели.

    :param raw_text: Исходный текст вакансии.
    :return: Структурированная вакансия.
    :raises ValueError: Если ответ модели пустой или невалидный.
    """
    ollama_client: AsyncOpenAI = get_ollama_async_client()

    response = await ollama_client.chat.completions.create(
        model=settings.ollama.llm_name,
        temperature=0,
        messages=[
            {"role": "system", "content": VACANCY_PROCESSING_SYSTEM_PROMPT},
            {"role": "user", "content": raw_text},
        ],
    )

    content = response.choices[0].message.content if response.choices else None
    if content is None or not content.strip():
        raise ValueError("Пустой ответ от языковой модели.")

    parsed_data = _parse_json_object(content=content)
    structured_data = VacancyStructuredData.model_validate(parsed_data)

    # Гарантируем сохранение исходного текста вакансии без изменений.
    if structured_data.raw_text != raw_text:
        structured_data = structured_data.model_copy(update={"raw_text": raw_text})

    return structured_data
