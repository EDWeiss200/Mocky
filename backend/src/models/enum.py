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


class Feature(str, Enum):
    RESUME_ANALYZE = "resume_analyze"
    RESUME_STATISTICS = "resume_statictics"
    GAP_ANALYZE = "gap_analyze"
    INTERVIEW_TEXT = "interview_text"
    INTERVIEW_VOICE = "interview_voice"

# стоимость фичей в токенах
FEATURE_COSTS = {
    Feature.RESUME_ANALYZE: 15,
    Feature.RESUME_STATISTICS : 5,
    Feature.GAP_ANALYZE: 10,
    Feature.INTERVIEW_TEXT: 2,
    Feature.INTERVIEW_VOICE: 5,
}


class PaymentTariffEnum(str, Enum):
    PRO = "pro"
    SPRINT = "sprint"
    TOKENS = "tokens"
