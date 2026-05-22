from enum import StrEnum


class RedisStreamName(StrEnum):
    VACANCY_PROCESSING = "vacancy_processing:vacancies"
    RESUME_PROCESSING = "resume_processing:resumes"
