from pydantic import BaseModel, Field


class MatchStructuredData(BaseModel):
    """Модель результата сопоставления резюме и вакансии."""

    score: float = Field(
        ...,
        description="Оценка соответствия от 0 до 100.",
        ge=0,
        le=100,
    )
    reasoning: str = Field(
        ...,
        description="Текстовое обоснование оценки с перечислением совпадающих и отсутствующих навыков.",
    )
