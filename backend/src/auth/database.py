from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import DATABASE_URL_CONFIG
from models.models import User as User_Base,OAuthAccount
import random


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
    yield CustomUserDatabase(session, User_Now, OAuthAccount)




class CustomUserDatabase(SQLAlchemyUserDatabase):
    async def create(self, create_dict: dict):
        
        if "username" not in create_dict:
            
            email = create_dict.get("email", "user")
            base_name = email.split("@")[0]
            
            
            create_dict["username"] = f"{base_name}_{random.randint(1000, 9999)}"
            

        return await super().create(create_dict)