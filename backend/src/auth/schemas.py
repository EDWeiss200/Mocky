import uuid
from pydantic import EmailStr
from typing import Optional
from fastapi_users import schemas
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime
from typing import List, Optional




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




