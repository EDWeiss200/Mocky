from utils.repository import AbstractRepository
import random
from database.redis import redis_client_forgotpass
from utils.worker import send_reset_code_email
from auth.auth import password_helper
from fastapi import HTTPException,status
from datetime import datetime, timezone,timedelta
from models.enum import Feature,FEATURE_COSTS
from models.models import User
import uuid

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

        cooldown_key = f"cooldown:forgot:{email}"

        ttl = await redis_client_forgotpass.ttl(cooldown_key)
        if ttl > 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Слишком много запросов. Подожди {ttl} секунд перед новой отправкой."
            )

        code = str(random.randint(100000,999999))

        reset_key = f"reset_code:{email}"

        await redis_client_forgotpass.setex(reset_key, 900, code)
        await redis_client_forgotpass.setex(cooldown_key, 60, "1")


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
    

    async def charge_for_feature(self, user: User, feature: Feature):
        now = datetime.now(timezone.utc)
        is_pro = user.subscription_tier == "pro" and user.subscription_expires_at and user.subscription_expires_at.replace(tzinfo=timezone.utc) > now
        is_sprint = user.subscription_tier == "sprint" and user.subscription_expires_at and user.subscription_expires_at.replace(tzinfo=timezone.utc) > now

        if is_pro:
            return 

        if is_sprint:
            if feature in [Feature.RESUME_ANALYZE, Feature.GAP_ANALYZE, Feature.INTERVIEW_TEXT]:
                return 
            if feature == Feature.INTERVIEW_VOICE:

                data_to_update = {
                    "sprint_voice_used" : user.sprint_voice_used + 1
                }

                await self.user_repo.update(user.id,data_to_update)
                return

        # если мы дошли сюда, значит это токены
        cost = FEATURE_COSTS.get(feature, 0)
        data_to_update = {
            "balance" : user.balance- cost
        }
        await self.user_repo.update(user.id,data_to_update)


    async def get_balance_info(self,user: User):

        user_token = user.balance
        user_tariff = user.subscription_tier

        subscription_expiries_at = user.subscription_expiries_at

        return {
            "user_token": user_token,
            "user_tariff": user_tariff,
            "subscription_expiries_at": subscription_expiries_at,
        }
    


    async def process_successful_payment(self, user_id: str, tariff: str, amount: int):

        user = await self.get_user_by_id(user_id)
        if not user:
            return

        now = datetime.now(timezone.utc)

        if tariff.startswith("tokens"):

            user.balance += amount
            
        elif tariff == "sprint":
            # активируем спринт на 3 дня и сбрасываем счетчик голоса
            user.subscription_tier = "sprint"
            user.subscription_expires_at = now + timedelta(days=3)
            user.sprint_voice_used = 0 
            
        elif tariff == "pro":
            # активируем PRO на 30 дней
            user.subscription_tier = "pro"
            user.subscription_expires_at = now + timedelta(days=30)

        # сохраняем обновленного юзера в базу
        await self.user_repo.update(user)



        
