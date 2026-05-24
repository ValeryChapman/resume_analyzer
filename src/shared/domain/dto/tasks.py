import json
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class VacancyProcessingTaskSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    vacancy_id: UUID


class ResumeProcessingTaskSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    resume_id: UUID


class MatchingTaskSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    resume_id: UUID | None = None


class NotificationEventType(StrEnum):
    MATCH_FOUND = "match_found"


class MatchFoundNotificationPayloadSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    match_result_id: UUID


class NotificationTaskSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_type: NotificationEventType
    payload: MatchFoundNotificationPayloadSchema

    @field_validator("payload", mode="before")
    @classmethod
    def parse_payload_json(
        cls, value: str | MatchFoundNotificationPayloadSchema | dict
    ) -> str | MatchFoundNotificationPayloadSchema | dict:
        if isinstance(value, str):
            return json.loads(value)
        return value
