from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class EducationLevel(str, Enum):
    SECONDARY = "secondary"
    HIGHER = "higher"
    UNKNOWN = "unknown"


class SeniorityLevel(str, Enum):
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    UNKNOWN = "unknown"


class VacancyStructuredData(BaseModel):
    title: str | None = Field(default=None, description="Название должности.")
    seniority: SeniorityLevel = Field(
        default=SeniorityLevel.UNKNOWN, description="Уровень позиции."
    )
    experience: float | None = Field(
        default=None,
        description="Минимальный опыт работы в годах.",
    )
    skills: list[str] = Field(
        default_factory=list,
        description="Список ключевых навыков и технологий.",
    )
    education: EducationLevel = Field(
        default=EducationLevel.UNKNOWN,
        description="Минимальный требуемый уровень образования.",
    )
    short_summary: str = Field(description="Краткая сводка вакансии.")
