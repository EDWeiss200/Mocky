from enum import Enum


class SessionStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"

class MessageRole(str, Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"

class InterviewRole(str, Enum):
    STRICT_SENIOR = "strict_senior"
    PRAGMATIC_LEAD = "pragmatic_lead"
    FRIENDLY_HR = "friendly_hr"
