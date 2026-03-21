from fastapi import APIRouter,Depends,Request,Response
from services.user_services import UserServices
from models.models import User
from schemas.schemas import UserReadSchema
from api.dependencies import user_service
from auth.auth import current_user
from fastapi_cache.decorator import cache

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
@cache(expire=60, key_builder=user_key_builder)
async def get_info_user(
    user: User = Depends(current_user),
    user_service: UserServices = Depends(user_service)
):

    user = await user_service.get_user_by_id(user.id)
    return user