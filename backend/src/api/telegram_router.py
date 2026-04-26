from fastapi import APIRouter,Depends,Header,HTTPException
from services.user_services import UserServices
from api.dependencies import user_service
from models.models import User
from schemas.schemas import TelegramLoginSchema,TelegramLinkRequest
from auth.auth import current_user,auth_backend
from auth.schemas import UserCreate
from auth.manager import UserManager, get_user_manager
from config import BOT_SECRET_TOKEN
import uuid
import secrets
from database.redis import redis_client_tgtoken
from config import BOT_NAME

router = APIRouter(
    tags=['telegram'],
    prefix='/telegram'
)

@router.post('/login')
async def login(
    data: TelegramLoginSchema,
    x_bot_token: str = Header(...),
    user_manager: UserManager = Depends(get_user_manager),
    strategy = Depends(auth_backend.get_strategy),
    user_service: UserServices = Depends(user_service)
):

    if x_bot_token != BOT_SECRET_TOKEN:
        raise HTTPException(status_code=403, detail = "Доступ запрещен")
    
    user = await user_service.get_user_by_tgid(data.telegram_id)

    if not user:

        unique_suffix = str(uuid.uuid4())[:8] 
        mock_email = f"tg_{data.telegram_id}_{unique_suffix}@mocky.com"
        mock_password = str(uuid.uuid4()) 
        
        user_create = UserCreate(
            email=mock_email,
            password=mock_password,
            username=data.username,
            
        )


        user = await user_manager.create(user_create)
        
        # И сразу же обновляем ему telegram_id через твой сервис
        await user_service.update_telegram_id(user.id, data.telegram_id)

    response = await auth_backend.login(strategy, user)
 
    return response 



@router.post("/link/generate")
async def generate_link(
    user: User = Depends(current_user)
):
    
    existing_token = await redis_client_tgtoken.get(f"user_tg_token:{user.id}")

    if existing_token:

        token = existing_token
    else:

        token = secrets.token_urlsafe(8)
        

        await redis_client_tgtoken.setex(f"tg_link:{token}", 600, str(user.id))

        await redis_client_tgtoken.setex(f"user_tg_token:{user.id}", 600, token)

    link = f"https://t.me/{BOT_NAME}?start={token}"

    return{
        "link":link,
        "token": token
    }


@router.post("/link/confirm")
async def confirm_link(
    data: TelegramLinkRequest,
    x_bot_token: str= Header(...),
    user_service: UserServices = Depends(user_service)
):
    
    if x_bot_token != BOT_SECRET_TOKEN:
        raise HTTPException(status_code=403, detail = "Доступ запрещен")
    
    user_id_str = await redis_client_tgtoken.get(f"tg_link:{data.token}")

    if not user_id_str:
        raise HTTPException(status_code=400, detail="Токен устарел или не существует")
    
    user_id = uuid.UUID(user_id_str)

    await user_service.update_telegram_id(user_id, data.telegram_id)

    await redis_client_tgtoken.delete(f"tg_link:{data.token}")
    await redis_client_tgtoken.delete(f"user_tg_token:{user_id}")

    return{
        "status": "success",
        "message": "Аккаунт успешно привязан"
    }


    