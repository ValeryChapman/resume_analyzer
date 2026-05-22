import re
from typing import Any

from pydantic import (
    AliasChoices,
    AliasPath,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class HHResumeSalarySchema(BaseModel):
    amount: int | None = Field(
        default=None, description="Желаемая зарплата в числовом виде."
    )
    currency: str | None = Field(default=None, description="Валюта желаемой зарплаты.")


class HHResumeExperienceItemSchema(BaseModel):
    organization_name: str | None = Field(
        default=None, description="Название организации из опыта работы."
    )
    positions: list[str] = Field(
        default_factory=list,
        description="Список должностей в рамках одной организации.",
    )


class HHResumeEducationSchema(BaseModel):
    education: str | None = Field(
        default=None, description="Уровень образования на русском языке."
    )
    institution_name: str | None = Field(
        default=None, description="Название учебного заведения."
    )
    direction: str | None = Field(
        default=None, description="Направление обучения, если оно указано."
    )


class HHResumeLanguageSchema(BaseModel):
    name: str | None = Field(
        default=None, description="Название языка (например, Английский)."
    )
    level: str | None = Field(
        default=None,
        description="Уровень владения (например, B2 — Средне-продвинутый).",
    )


class HHResumeDetailResponseSchema(BaseModel):
    id: str | None = Field(default=None, description="Уникальный идентификатор...")
    title: str | None = Field(default=None, description="Заголовок резюме...")
    url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("url", "alternate_url"),
        description="Публичный URL резюме.",
    )
    last_name: str | None = Field(default=None, description="Фамилия кандидата.")
    first_name: str | None = Field(default=None, description="Имя кандидата.")
    area: str | None = Field(
        default=None,
        validation_alias=AliasPath("area", "name"),
        description="Город кандидата.",
    )
    age: int | None = Field(default=None, description="Возраст кандидата.")
    gender: str | None = Field(
        default=None,
        validation_alias=AliasPath("gender", "name"),
        description="Пол кандидата.",
    )
    total_experience: int | None = Field(
        default=None,
        validation_alias=AliasPath("total_experience", "months"),
        description="Общий опыт работы в месяцах.",
    )
    experience: list[HHResumeExperienceItemSchema] = Field(
        default_factory=list,
        description="Список организаций с перечнем должностей кандидата.",
    )
    skills: list[str] = Field(
        default_factory=list,
        description="Объединенный список навыков из полей skills и skill_set.",
    )
    education: list[HHResumeEducationSchema] = Field(
        default_factory=list,
        description="Список образовательных учреждений кандидата.",
    )
    salary: HHResumeSalarySchema | None = Field(
        default=None,
        description="Желаемая зарплата и ее валюта.",
    )
    professional_roles: list[str] = Field(
        default_factory=list,
        description="Список профессиональных ролей кандидата.",
    )
    languages: list[HHResumeLanguageSchema] = Field(
        default_factory=list,
        validation_alias=AliasChoices("language", "languages"),
        description="Список языков и уровень владения ими.",
    )

    model_config = ConfigDict(populate_by_name=True)

    @model_validator(mode="before")
    @classmethod
    def _merge_skills(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        combined_skills = []
        if isinstance(raw_skills := data.get("skills"), str):
            combined_skills.append(raw_skills)

        if isinstance(skill_set := data.get("skill_set"), list):
            combined_skills.extend(s for s in skill_set if isinstance(s, str))

        if combined_skills:
            split_skills = (
                item.strip()
                for chunk in combined_skills
                for item in re.split(r"[,;\n]+", chunk)
                if item.strip()
            )
            data["skills"] = list(dict.fromkeys(split_skills))
        else:
            data["skills"] = []

        return data

    @field_validator("experience", mode="before")
    @classmethod
    def _parse_experience(cls, experience: Any) -> Any:
        if not isinstance(experience, list):
            return experience

        grouped: dict[str | None, dict[str, Any]] = {}
        for item in experience:
            if not isinstance(item, dict):
                continue

            org_name = item.get("company")
            if not isinstance(org_name, str) or not org_name.strip():
                employer = item.get("employer")
                org_name = employer.get("name") if isinstance(employer, dict) else None

            org_name = (
                org_name.strip()
                if isinstance(org_name, str) and org_name.strip()
                else None
            )

            position = item.get("position")
            position = (
                position.strip()
                if isinstance(position, str) and position.strip()
                else None
            )

            group = grouped.setdefault(
                org_name, {"organization_name": org_name, "positions": {}}
            )
            if position:
                group["positions"][position] = None

        return [
            {
                "organization_name": g["organization_name"],
                "positions": list(g["positions"]),
            }
            for g in grouped.values()
        ]

    @field_validator("education", mode="before")
    @classmethod
    def _parse_education(cls, education: Any) -> Any:
        if not isinstance(education, dict):
            return []

        # 1. Достаем общий (корневой) уровень образования как fallback
        fallback_level_name = None
        if isinstance(top_level := education.get("level"), dict):
            fallback_level_name = (
                lvl.strip()
                if isinstance(lvl := top_level.get("name"), str) and lvl.strip()
                else None
            )

        parsed_education = []

        # 2. Идем по массиву конкретных учебных заведений
        if isinstance(primary := education.get("primary"), list):
            for item in primary:
                if not isinstance(item, dict):
                    continue

                # Пробуем взять уровень из конкретного заведения, иначе используем fallback
                level_name = fallback_level_name
                if isinstance(item_level := item.get("education_level"), dict):
                    if isinstance(name := item_level.get("name"), str) and name.strip():
                        level_name = name.strip()

                # Извлекаем название вуза
                inst_name = (
                    inst.strip()
                    if isinstance(inst := item.get("name"), str) and inst.strip()
                    else None
                )

                # Извлекаем специальность/направление (в HH это поле organization)
                direction = (
                    drc.strip()
                    if isinstance(drc := item.get("organization"), str) and drc.strip()
                    else None
                )

                if any((level_name, inst_name, direction)):
                    parsed_education.append(
                        {
                            "education": level_name,
                            "institution_name": inst_name,
                            "direction": direction,
                        }
                    )

        return parsed_education

    @field_validator("professional_roles", mode="before")
    @classmethod
    def _parse_professional_roles(cls, roles: Any) -> Any:
        if not isinstance(roles, list):
            return roles

        return [
            stripped_name
            for role in roles
            if isinstance(role, dict)
            and isinstance(name := role.get("name"), str)
            and (stripped_name := name.strip())
        ]

    @field_validator("languages", mode="before")
    @classmethod
    def _parse_languages(cls, languages: Any) -> Any:
        if not isinstance(languages, list):
            return languages

        parsed_languages = []
        for lang in languages:
            if not isinstance(lang, dict):
                continue

            name = (
                n.strip()
                if isinstance(n := lang.get("name"), str) and n.strip()
                else None
            )

            level = None
            if isinstance(lvl := lang.get("level"), dict):
                level = (
                    l_name.strip()
                    if isinstance(l_name := lvl.get("name"), str) and l_name.strip()
                    else None
                )

            if name or level:
                parsed_languages.append({"name": name, "level": level})

        return parsed_languages
