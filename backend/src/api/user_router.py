from fastapi import APIRouter,Depends,Request,Response
from services.user_services import UserServices
from models.models import User
from schemas.schemas import UserReadSchema,ResetPasswordRequest
from api.dependencies import user_service
from auth.auth import current_user
from fastapi_cache.decorator import cache
from pydantic import EmailStr
from auth.auth import get_user_manager
from fastapi import HTTPException
from database.redis import redis_client_forgotpass



def user_key_builder(
    func,
    namespace: str = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    # достаем пользователя из зависимостей
    user = kwargs.get("user") 
    user_id = str(user.id) if user else "anonymous"
    # делаем уникальный ключ: путь + id юзера
    return f"{namespace}:{request.url.path}:{user_id}"

router = APIRouter(
    tags=['user'],
    prefix='/users'
)


@router.get('')
#@cache(expire=60, key_builder=user_key_builder)
async def get_info_user(
    user: User = Depends(current_user),
    user_service: UserServices = Depends(user_service)
):

    user = await user_service.get_user_by_id(user.id)
    return user

@router.patch('/username')
async def update_username(
    username: str,
    user: User = Depends(current_user),
    user_service: UserServices = Depends(user_service)
):
    await user_service.update_username(user.id,username)

    return {
        f"Имя пользователя измененно на {username}"
    }

@router.post("/forgot-password")
async def forgot_password(
    email: EmailStr, 
    user_service: UserServices = Depends(user_service)
):
    user = await user_service.get_user_by_email(email)

    if not user:
        return {"message": "Если такой email зарегестрирован, мы отправимли код"}
    
    res = await user_service.send_code_forgotpass(email)


@router.post("/reset-password")
async def reset_password(
    data: ResetPasswordRequest,
    user_service: UserServices = Depends(user_service)
):
    
    user = await user_service.get_user_by_email(data.email)
    if not user:
         raise HTTPException(status_code=404, detail="Пользователь не найден")


    res = await user_service.reset_password(user.id,data.code,data.new_password,data.email)

    return res
    