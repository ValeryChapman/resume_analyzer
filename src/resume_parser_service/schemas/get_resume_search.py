from pydantic import BaseModel, Field


class HHResumeSearchItemSchema(BaseModel):
    id: str = Field(..., description="Уникальный идентификатор резюме в HeadHunter.")
    url: str | None = Field(
        default=None,
        description="URL детальной ручки HeadHunter для получения полного резюме.",
    )


class HHResumeSearchResponseSchema(BaseModel):
    items: list[HHResumeSearchItemSchema] = Field(
        ...,
        description="Список резюме, найденных HeadHunter по заданным фильтрам.",
    )
