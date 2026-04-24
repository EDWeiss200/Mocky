import uuid
from pydantic import EmailStr
from typing import Optional
from fastapi_users import schemas
from uuid import UUID




class UserRead(schemas.BaseUser[uuid.UUID]):
    id: UUID
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




