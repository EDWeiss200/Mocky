from pydantic import BaseModel,EmailStr,Field,FileUrl
from sqlalchemy import Date
from fastapi import UploadFile
from enum import Enum
from typing import Optional
from datetime import datetime



class UserReadSchema(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True



