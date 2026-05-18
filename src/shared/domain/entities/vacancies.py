from enum import Enum

from pydantic import BaseModel, Field


class SeniorityLevel(str, Enum):
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    UNKNOWN = "unknown"


class EducationLevel(str, Enum):
    SECONDARY = "secondary"
    HIGHER = "higher"
    UNKNOWN = "unknown"


class VacancyStructuredData(BaseModel):
    """Модель структурированных данных вакансии, извлеченных из текста."""

    title: str = Field(
        ..., description="Название должности из текста, например Python разработчик."
    )
    seniority: SeniorityLevel | None = Field(
        default=None, description="Уровень позиции."
    )
    experience: int | None = Field(
        default=None,
        description="Минимальный опыт работы в годах, если указан явно, иначе null.",
    )
    skills: list[str] = Field(
        ...,
        description="Список явно указанных профессиональных навыков, компетенций, программного обеспечения, оборудования или методологий.",
    )
    education: EducationLevel | None = Field(
        default=None, description="Требуемый уровень образования."
    )
    summary: str = Field(
        ...,
        description="Одно короткое предложение на русском с кратким описанием вакансии.",
    )
