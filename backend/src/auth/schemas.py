import uuid
from pydantic import EmailStr
from typing import Optional
from fastapi_users import schemas
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import List, Optional
from enum import Enum
from models.models import SessionStatus, MessageRole


class UserRead(schemas.BaseUser[int]):
    id: int 
    username : str
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False

class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    username : str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


# --- Схемы для Message ---
class MessageBase(BaseModel):
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
    resume_id: int

class InterviewRead(InterviewBase):
    id: int
    user_id: int
    resume_id: int
    created_at: datetime
    # Если захочешь отдавать интервью сразу с сообщениями:
    # messages: List[MessageRead] = []
    
    model_config = ConfigDict(from_attributes=True)
