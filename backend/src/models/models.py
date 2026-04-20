from typing import Annotated, List, Optional
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo  # <--- Ключевое исправление здесь!
from models.enum import SessionStatus,MessageRole


from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, MetaData
from fastapi_users.db import SQLAlchemyBaseUserTableUUID,SQLAlchemyBaseOAuthAccountTableUUID
from schemas.schemas import UserReadSchema
from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy import Uuid
import uuid

# Настройки для ID
uuidpk = Annotated[uuid.UUID, mapped_column(
    Uuid(as_uuid=True), 
    primary_key=True, 
    default=uuid.uuid4
)]

msk_tz = timezone(timedelta(hours=3), name="MSK")

class Base(DeclarativeBase):
    pass

class OAuthAccount(SQLAlchemyBaseOAuthAccountTableUUID, Base):
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="cascade"), 
        nullable=False
    )


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    id: Mapped[uuidpk]
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    telegram_id: Mapped[Optional[str | None]] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    oauth_accounts: Mapped[List[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined", cascade="all, delete-orphan"
    )

    balance: Mapped[int] = mapped_column(Integer,default=50) 
    subscription_tier: Mapped[str] = mapped_column(String,default="free")
    subscription_expiries_at: Mapped[datetime] = mapped_column(nullable=True)   
    sprint_voice_used: Mapped[int] = mapped_column(Integer,default=0) 

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    resumes: Mapped[List["Resume"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    interviews: Mapped[List["Interview"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def to_read_model(self) -> UserReadSchema:
        return UserReadSchema(
            id=self.id,
            username=self.username,
            email=self.email,
        )



class Resume(Base):
    __tablename__ = "resumes"
    id: Mapped[uuidpk]
    name: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    raw_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
    default=lambda: datetime.now(msk_tz).replace(tzinfo=None)
    )   
    user: Mapped["User"] = relationship(back_populates="resumes")
    interviews: Mapped[List["Interview"]] = relationship(back_populates="resume")

class Interview(Base):
    __tablename__ = "interviews"
    id: Mapped[uuidpk]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    resume_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resumes.id", ondelete="CASCADE"))
    vacancy_context: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(String, default="pragmatic_lead")
    number_question: Mapped[Optional[int] | 5] = mapped_column(Integer)
    status: Mapped[SessionStatus] = mapped_column(default=SessionStatus.PLANNED)
    prep_plan: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    total_score: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
    default=lambda: datetime.now(msk_tz).replace(tzinfo=None)
    )
    skills_score: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    
    user: Mapped["User"] = relationship(back_populates="interviews")
    resume: Mapped["Resume"] = relationship(back_populates="interviews")
    messages: Mapped[List["Message"]] = relationship(back_populates="interview", cascade="all, delete-orphan")



class Message(Base):
    __tablename__ = "messages"
    id: Mapped[uuidpk]
    interview_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("interviews.id"))
    role: Mapped[MessageRole] = mapped_column()
    content: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
    default=lambda: datetime.now(msk_tz).replace(tzinfo=None)
    )
    interview: Mapped["Interview"] = relationship(back_populates="messages")


