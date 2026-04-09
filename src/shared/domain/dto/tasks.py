from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VacancyProcessingTaskSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    vacancy_id: UUID
