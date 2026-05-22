import json
from functools import cache

from openai import AsyncOpenAI
from pydantic import ValidationError

from matching_service.settings import settings
from shared.domain.entities.matches import MatchStructuredData
from shared.infrastructure.llm.client import get_llm_async_client

MATCHING_SYSTEM_PROMPT = """
Вы – высококвалифицированный HR-аналитик. Ваша задача – оценить степень соответствия резюме кандидата требованиям конкретной вакансии.

Методология оценки (Score 0-100):
1. Hard Skills (40%): Сравните технические навыки, инструменты и технологии. Учитывайте как полное совпадение, так и владение аналогичными стеками.
2. Опыт работы (30%): Соответствие стажа (в годах) и релевантность предыдущих ролей/проектов.
3. Seniority Level (15%): Соответствие уровня квалификации (Junior, Middle, Senior).
4. Образование и достижения (15%): Соответствие уровня образования и значимость указанных достижений.

Правила формирования ответа:
- score: Число от 0 до 100.
- reasoning: Подробное обоснование на русском языке. Укажите:
    - Какие ключевые навыки совпали.
    - Каких критических навыков не хватает.
    - Сильные и слабые стороны кандидата относительно данной вакансии.
    - Вывод о пригодности.

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
    schema = MatchStructuredData.model_json_schema()
    schema_str = json.dumps(schema, ensure_ascii=False, indent=2)
    return f"{MATCHING_SYSTEM_PROMPT}\n\nОЖИДАЕМАЯ JSON-СХЕМА:\n{schema_str}"


def _build_user_prompt(
    vacancy_text: str,
    vacancy_structured: dict,
    resume_text: str,
    resume_structured: dict,
) -> str:
    """
    Формирует пользовательский промпт со всеми данными.

    :param vacancy_text: Сырой текст вакансии.
    :param vacancy_structured: Структурированные данные вакансии.
    :param resume_text: Сырой текст резюме.
    :param resume_structured: Структурированные данные резюме.
    :return: Готовый пользовательский промпт.
    """
    return f"""
ДАННЫЕ ВАКАНСИИ:
- Структурированные требования: {json.dumps(vacancy_structured, ensure_ascii=False)}
- Полный текст: {vacancy_text}

ДАННЫЕ РЕЗЮМЕ:
- Структурированные данные: {json.dumps(resume_structured, ensure_ascii=False)}
- Полный текст: {resume_text}
""".strip()


async def calculate_match_score_service(
    vacancy_text: str,
    vacancy_structured: dict,
    resume_text: str,
    resume_structured: dict,
) -> MatchStructuredData:
    """
    Вычисляет оценку соответствия с помощью LLM.

    :param vacancy_text: Сырой текст вакансии.
    :param vacancy_structured: Структурированные данные вакансии.
    :param resume_text: Сырой текст резюме.
    :param resume_structured: Структурированные данные резюме.
    :return: Результат обработки.
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
            {
                "role": "user",
                "content": _build_user_prompt(
                    vacancy_text=vacancy_text,
                    vacancy_structured=vacancy_structured,
                    resume_text=resume_text,
                    resume_structured=resume_structured,
                ),
            },
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
        return MatchStructuredData.model_validate(parsed_data)
    except ValidationError as exc:
        raise ValueError(f"Невалидный структурированный ответ модели: {exc}") from exc
