import uuid
from pydantic import EmailStr
from typing import Optional
from fastapi_users import schemas
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from models.enum import SessionStatus,MessageRole

class UserReadSchema(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True



# --- Схемы для Message ---
class MessageBase(BaseModel):
    interview_id: int
    role: MessageRole
    content: str

class MessageCreate(MessageBase):
    pass

class MessageRead(MessageBase):
    id: int
    interview_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Схемы для Resume ---
class ResumeBase(BaseModel):
    raw_text: str

class ResumeCreate(ResumeBase):
    pass

class ResumeRead(ResumeBase):
    id: int
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Схемы для Interview ---
class InterviewBase(BaseModel):
    status: SessionStatus = SessionStatus.PLANNED
    total_score: Optional[int] = None

class InterviewCreate(InterviewBase):
    user_id:int
    resume_id: int


class InterviewRead(InterviewBase):
    id: int
    user_id: int
    resume_id: int
    created_at: datetime
    # Если захочешь отдавать интервью сразу с сообщениями:
    # messages: List[MessageRead] = []
    
    model_config = ConfigDict(from_attributes=True)


class StartInterviewRequest(BaseModel):
    resume_id: int
    
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class AnswerRequest(BaseModel):
    answer_text: str
    
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)