from services.user_services import UserServices
from repositories.user_repo import UserRepository


def user_service() -> UserServices:
    return UserServices(UserRepository)
