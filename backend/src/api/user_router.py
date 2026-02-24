from fastapi import APIRouter,Depends
from services.user_services import UserServices
from models.models import User
from schemas.schemas import UserReadSchema
from api.dependencies import user_service
from auth.auth import current_user


router = APIRouter(
    tags=['user'],
    prefix='/users'
)

@router.get('')
async def get_info_user(
    user: User = Depends(current_user),
    user_service: UserServices = Depends(user_service)
):

    user = await user_service.get_user_by_id(user.id)
    return user