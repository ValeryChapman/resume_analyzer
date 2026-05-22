from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VacancyProcessingTaskSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    vacancy_id: UUID


class ResumeProcessingTaskSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    resume_id: UUID


class MatchingTaskSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    resume_id: UUID | None = None
