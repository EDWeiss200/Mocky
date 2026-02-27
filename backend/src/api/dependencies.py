from services.user_services import UserServices
from repositories.user_repo import UserRepository

from services.resume_services import ResumeServices
from repositories.resume_repo import ResumeRepository


def user_service() -> UserServices:
    return UserServices(UserRepository)

def resume_service() -> ResumeServices:
    return ResumeServices(ResumeRepository)