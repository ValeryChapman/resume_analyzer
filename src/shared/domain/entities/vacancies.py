from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class RequirementImportance(str, Enum):
    REQUIRED = "required"
    PREFERRED = "preferred"


class EducationLevel(str, Enum):
    HIGHER = "higher"
    UNKNOWN = "unknown"


class SeniorityLevel(str, Enum):
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    UNKNOWN = "unknown"


class SkillRequirement(BaseModel):
    name: str = Field(description="Название навыка.")
    importance: RequirementImportance = Field(
        default=RequirementImportance.REQUIRED,
        description="Важность навыка для вакансии.",
    )


class ExperienceRequirement(BaseModel):
    min_years_total: float | None = Field(
        default=None, description="Минимальный общий опыт работы в годах."
    )


class EducationRequirement(BaseModel):
    required: bool = Field(
        default=False, description="Требуется ли образование для вакансии."
    )
    level: EducationLevel = Field(
        default=EducationLevel.UNKNOWN,
        description="Минимальный требуемый уровень образования.",
    )


class VacancyStructuredData(BaseModel):
    title: str | None = Field(default=None, description="Название должности.")
    seniority: SeniorityLevel = Field(
        default=SeniorityLevel.UNKNOWN, description="Требуемый уровень seniority."
    )
    experience: ExperienceRequirement = Field(
        default_factory=ExperienceRequirement, description="Требования к опыту работы."
    )
    required_skills: list[SkillRequirement] = Field(
        default_factory=list, description="Список обязательных навыков."
    )
    preferred_skills: list[SkillRequirement] = Field(
        default_factory=list, description="Список желательных навыков."
    )
    education: EducationRequirement = Field(
        default_factory=EducationRequirement, description="Требования к образованию."
    )
    short_summary: str = Field(description="Краткая сводка вакансии.")
    raw_text: str = Field(description="Исходный текст вакансии.")
