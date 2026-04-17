from utils.repository import AbstractRepository
import random
from database.redis import redis_client_forgotpass
from utils.worker import send_reset_code_email
from auth.auth import password_helper
from fastapi import HTTPException

class UserServices:

    def __init__(self,user_repo: AbstractRepository) -> None:
        self.user_repo = user_repo()

    async def get_user_by_id(self,user_id):

        filters = [
            self.user_repo.model.id == user_id
        ]

        user = await self.user_repo.find_filter_drm(filters)

        

        return user
    

    async def get_user_by_email(self,email):

        filters = [
            self.user_repo.model.email == email
        ]

        user = await self.user_repo.find_filter_drm(filters)

        return user
    
    

    async def get_user_by_tgid(self,telegram_id):

        filters = [
            self.user_repo.model.telegram_id == telegram_id
        ]

        user = await self.user_repo.find_filter_drm(filters)

        return user
    


    async def update_telegram_id(self,user_id,telegram_id):



        filters = [
            self.user_repo.model.telegram_id == telegram_id
        ]
        user = await self.user_repo.find_filter_drm(filters)

        if user:
            await self.user_repo.delete_one(user.id)
    


        data_to_update = {
            "telegram_id": telegram_id,
        }

        user = await self.user_repo.update(user_id,data_to_update)


    async def update_username(self,user_id,new_username):

        data_to_update ={
            "username":new_username
        }

        await self.user_repo.update(user_id,data_to_update)

    async def send_code_forgotpass(self,email):

        code = str(random.randint(100000,999999))

        await redis_client_forgotpass.setex(f"reset_code:{email}", 900, code)

        # кидаем задачу в Celery: метод delay делает это асинхронно для FastAPI
        send_reset_code_email.delay(email, code)

        return {"message": "Код отправлен на почту"}
    
    async def reset_password(self,user_id,code,new_password,email):

        saved_code = await redis_client_forgotpass.get(f"reset_code:{email}")
    
        if not saved_code or saved_code != code:
            raise HTTPException(status_code=400, detail="Неверный или устаревший код")

        hashed_password = password_helper.hash(new_password)

        data_to_update = {
            "hashed_password": hashed_password
        }

        user = await self.user_repo.update(user_id,data_to_update)

        await redis_client_forgotpass.delete(f"reset_code:{email}")

        return {"message": "Пароль успешно изменен"}



        
