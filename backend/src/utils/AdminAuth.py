from models.models import User
from database.database import async_session_maker
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from sqlalchemy import select
from auth.auth import password_hash


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        async with async_session_maker() as session:
            query = select(User).where(User.email == email)
            result = await session.execute(query)
            user = result.scalars().first()

            # Проверяем, существует ли юзер и есть ли у него права суперадмина
            if not user or not user.is_superuser:
                return False
            
            # Сверяем введенный пароль с хэшем из БД
            is_valid_password = password_hash.verify(password, user.hashed_password)
            if not is_valid_password:
                return False
            
            # Авторизация успешна — сохраняем ID пользователя в защищенную куку
            request.session.update({"admin_token": str(user.id)})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("admin_token")
        if not token:
            return False
            
        async with async_session_maker() as session:
            # Проверяем токен (в нашем случае это ID)
            query = select(User).where(User.id == token)
            result = await session.execute(query)
            user = result.scalars().first()
            
            # Убеждаемся, что юзер все еще существует и у него не забрали права
            if not user or not user.is_superuser:
                return False
                
        return True