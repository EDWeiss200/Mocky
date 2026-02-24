from typing import AsyncGenerator
from sqlalchemy import Boolean, ForeignKey, Integer, String, func, select,Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase,relationship
from config import DATABASE_URL_CONFIG
from models.models import User as User_Base

DATABASE_URL = DATABASE_URL_CONFIG


class Base(DeclarativeBase):
    pass


class User_Now(User_Base):
    ...



engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)



async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User_Now)