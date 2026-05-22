from typing import Any

from resume_parser_service.schemas.get_resume_detail import HHResumeDetailResponseSchema


def format_resume_details_to_text(resume: HHResumeDetailResponseSchema) -> str:
    """
    Преобразует структурированные данные резюме в текстовое описание.
    """

    def get_val(val: Any, default: str = "Не указано") -> Any:
        return val if val not in (None, "", []) else default

    # Формируем строку имени
    full_name = f"{resume.first_name or ''} {resume.last_name or ''}".strip()
    if not full_name:
        full_name = "Не указано"

    # Основная информация
    lines = [
        f"Название резюме: {get_val(resume.title)}",
        f"Имя: {full_name}",
        f"Возраст: {get_val(resume.age)}, Пол: {get_val(resume.gender)}, Город: {get_val(resume.area)}",
        f"Желаемая зарплата: {resume.salary.amount if resume.salary and resume.salary.amount else 'Не указано'} "
        f"{resume.salary.currency if resume.salary and resume.salary.currency else ''}".strip(),
        f"Профессиональные роли: {', '.join(resume.professional_roles) if resume.professional_roles else 'Не указано'}",
        f"Общий опыт работы: {get_val(resume.total_experience)} мес.",
        "",
        "Опыт работы:",
    ]

    # Опыт работы
    if resume.experience:
        for exp in resume.experience:
            org_name = get_val(exp.organization_name)
            positions = ", ".join(exp.positions) if exp.positions else "Не указано"
            lines.append(f"- Организация: {org_name}")
            lines.append(f"  Должности: {positions}")
    else:
        lines.append("Не указано")

    # Навыки
    lines.extend(
        [
            "",
            f"Ключевые навыки: {', '.join(resume.skills) if resume.skills else 'Не указано'}",
        ]
    )

    # Образование
    lines.extend(["", "Образование:"])
    if resume.education:
        for edu in resume.education:
            lines.append(f"- Уровень: {get_val(edu.education)}")
            lines.append(f"  Учебное заведение: {get_val(edu.institution_name)}")
            lines.append(f"  Направление: {get_val(edu.direction)}")
    else:
        lines.append("Не указано")

    # Языки
    lines.extend(["", "Владение языками:"])
    if resume.languages:
        for lang in resume.languages:
            name = get_val(lang.name)
            level = get_val(lang.level)
            lines.append(f"- {name} ({level})")
    else:
        lines.append("Не указано")

    return "\n".join(lines)
