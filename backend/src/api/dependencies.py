from services.user_services import UserServices
from repositories.user_repo import UserRepository

from services.resume_services import ResumeServices
from repositories.resume_repo import ResumeRepository

from services.interview_services import InterviewServices
from repositories.interview_repo import InterviewRepository

from services.message_services import MessageServices
from repositories.message_repo import MessageRepository

from services.telegram_services import TelegramService

from services.HeadHunter_services import HeadHunterService

from fastapi import HTTPException
from datetime import datetime, timezone
from models.models import User

async def verify_balance(user: User, cost: int):

    if user.subscription_tier != "free" and user.subscription_expires_at:
        if user.subscription_expires_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc):
            return True 

    if user.balance >= cost:
        return True
        
    raise HTTPException(
        status_code=402, 
        detail="Не хватает токенов или нужна подписка"
    )


def user_service() -> UserServices:
    return UserServices(UserRepository)

def resume_service() -> ResumeServices:
    return ResumeServices(ResumeRepository)

def interview_service() -> InterviewServices:
    return InterviewServices(InterviewRepository)

def message_service() -> MessageServices:
    return MessageServices(MessageRepository)

def telegram_service() -> TelegramService:
    return TelegramService()

def headhunter_service() -> HeadHunterService:
    return HeadHunterService()



