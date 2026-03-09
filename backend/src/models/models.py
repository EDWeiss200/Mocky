from typing import Annotated, List, Optional
from datetime import datetime, timezone  # <--- Ключевое исправление здесь!
from models.enum import SessionStatus,MessageRole

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, MetaData
from fastapi_users.db import SQLAlchemyBaseUserTable
from schemas.schemas import UserReadSchema

# Настройки для ID
intpk = Annotated[int, mapped_column(index=True, primary_key=True)]

class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "users"
    id: Mapped[intpk]
    username: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    telegram_id: Mapped[Optional[int]] = mapped_column(unique=True)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
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
    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    raw_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
    default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )   
    user: Mapped["User"] = relationship(back_populates="resumes")
    interviews: Mapped[List["Interview"]] = relationship(back_populates="resume")

class Interview(Base):
    __tablename__ = "interviews"
    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    status: Mapped[SessionStatus] = mapped_column(default=SessionStatus.PLANNED)
    total_score: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
    default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    user: Mapped["User"] = relationship(back_populates="interviews")
    resume: Mapped["Resume"] = relationship(back_populates="interviews")
    messages: Mapped[List["Message"]] = relationship(back_populates="interview", cascade="all, delete-orphan")



class Message(Base):
    __tablename__ = "messages"
    id: Mapped[intpk]
    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id"))
    role: Mapped[MessageRole] = mapped_column()
    content: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
    default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    interview: Mapped["Interview"] = relationship(back_populates="messages")