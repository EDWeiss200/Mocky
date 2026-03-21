from services.user_services import UserServices
from repositories.user_repo import UserRepository

from services.resume_services import ResumeServices
from repositories.resume_repo import ResumeRepository

from services.interview_services import InterviewServices
from repositories.interview_repo import InterviewRepository

from services.message_services import MessageServices
from repositories.message_repo import MessageRepository

from services.telegram_services import TelegramService



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


