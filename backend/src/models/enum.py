from enum import Enum


class SessionStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"

class MessageRole(str, Enum):
    SYSTEM = "system"
    ASSISTANT = "assistant"
    USER = "user"

