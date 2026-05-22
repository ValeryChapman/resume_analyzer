from enum import Enum


class SeniorityLevel(str, Enum):
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    UNKNOWN = "unknown"


class EducationLevel(str, Enum):
    SECONDARY = "secondary"
    HIGHER = "higher"
    UNKNOWN = "unknown"
