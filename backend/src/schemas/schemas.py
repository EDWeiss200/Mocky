import uuid
from pydantic import EmailStr
from typing import Optional
from fastapi_users import schemas
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr,HttpUrl
from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel
from models.enum import SessionStatus,MessageRole, InterviewRole

from uuid import UUID

class UserReadSchema(BaseModel):
    id: UUID
    username: str
    email: EmailStr

    class Config:
        from_attributes = True





# --- Схемы для Message ---
class MessageBase(BaseModel):
    interview_id: UUID
    role: MessageRole
    content: str

class MessageCreate(MessageBase):
    pass

class MessageRead(MessageBase):
    id: UUID
    interview_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Схемы для Resume ---
class ResumeBase(BaseModel):
    raw_text: str

class ResumeCreate(ResumeBase):
    pass

class ResumeRead(ResumeBase):
    id: UUID
    user_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Схемы для Interview ---
class InterviewBase(BaseModel):
    status: SessionStatus = SessionStatus.PLANNED
    total_score: Optional[int] = None

class InterviewCreate(InterviewBase):
    user_id: UUID
    resume_id: UUID
    status: SessionStatus
    number_question: int | None = 5
    role: InterviewRole = InterviewRole.PRAGMATIC_LEAD
    prep_plan: List[str] | None = None
    vacancy_context: str | None = None


class InterviewRead(InterviewBase):
    id: UUID
    user_id: int
    resume_id: UUID
    created_at: datetime
    # Если захочешь отдавать интервью сразу с сообщениями:
    # messages: List[MessageRead] = []
    
    model_config = ConfigDict(from_attributes=True)


class StartInterviewRequest(BaseModel):
    resume_id: UUID
    number_question: int
    role: InterviewRole = InterviewRole.PRAGMATIC_LEAD
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class AnswerRequest(BaseModel):
    answer_text: str
    
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class TelegramLoginSchema(BaseModel):
    telegram_id: str
    username: str

class TelegramLinkRequest(BaseModel):
    telegram_id: str
    token: str


class StartHHInterviewRequest(BaseModel):
    resume_id: UUID 
    hh_url: HttpUrl
    number_question: int | None = 5
    role: InterviewRole = InterviewRole.PRAGMATIC_LEAD


class GapAnalysisResponse(BaseModel):
    match_percentage: int
    matched_skills: List[str]
    missing_skills: List[str]
    warning: str


class ResumeAnalysisResponse(BaseModel):
    estimated_grade: str         
    market_demand_score: int      
    strong_points: List[str]      
    red_flags: List[str]          
    recommendations: List[str]