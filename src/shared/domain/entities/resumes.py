from pydantic import BaseModel, Field

from shared.domain.entities.common import EducationLevel, SeniorityLevel


class ResumeStructuredData(BaseModel):
    """Модель структурированных данных резюме, извлеченных из текста."""

    title: str = Field(
        ...,
        description="Желаемая должность или текущая роль, например, Python разработчик.",
    )
    seniority: SeniorityLevel | None = Field(
        default=None, description="Уровень квалификации кандидата."
    )
    experience: int | None = Field(
        default=None,
        description="Общий стаж работы в годах, если указан явно, иначе null.",
    )
    skills: list[str] = Field(
        ...,
        description="Список технических навыков, инструментов и компетенций.",
    )
    education: EducationLevel | None = Field(
        default=None, description="Уровень образования кандидата."
    )
    achievements: list[str] = Field(
        default_factory=list,
        description="Ключевые достижения и результаты работы.",
    )
    summary: str = Field(
        ...,
        description="Профессиональная сводка (1-2 предложения), сжатое описание кандидата на русском языке.",
    )
