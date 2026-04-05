from config import config
import aiohttp
import json
from redis.asyncio import Redis

class Backend_Client():

    def __init__(self, base_url : str, redis_client: Redis):
        self.base_url = base_url
        self.redis = redis_client
        self.session = aiohttp.ClientSession()
    
    async def close(self):
        await self.session.close()

    async def _get_auth_headers(self, user_id: int) -> dict:
        """Достаем куку из Redis (База 3) и готовим хедеры"""
        cookie = await self.redis.get(f"auth_sid:{user_id}")
        headers = {}
        if cookie:
            headers["Cookie"] = cookie
        return headers


    
        # Логин(создание нового акка в бд на основе тг акка)
    async def login(self, telegram_id: int, username: str):
        url = f"{self.base_url}/telegram/login"
        
        # Данные из твоего скриншота Swagger
        headers = {
            "x-bot-token": config.BOT_SECRET_TOKEN, # Берем из конфига
            "Content-Type": "application/json"
        }
        payload = {"telegram_id": int(telegram_id), "username": username}
        
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status in [200, 204]:
                # Сохраняем куку сессии в Redis
                set_cookie = response.headers.get("Set-Cookie")
                if set_cookie:
                    # Оставляем только 'session=xyz', убираем path и прочее
                    clean_cookie = set_cookie.split(';')[0]
                    await self.redis.set(f"auth_sid:{telegram_id}", clean_cookie, ex=86400)
                return True
            print(f"Ошибка логина {response.status}: {await response.text()}")
            return False



    async def send_message(self, user_id: int, answerText: str, interview_id: int):
        url = f"{self.base_url}/interviews/answer/{interview_id}"
        headers = await self._get_auth_headers(user_id)
        
        payload = {"answerText": answerText}
        
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("answer", "Бэкенд не прислал текст ответа")
            return "Ошибка: Не удалось получить ответ от интервьюера"
            

    # Функция загрузки резюме, работает только после связки аккаунтов
    async def resume_upload(self, user_id: int, file_bytes: bytes, file_name: str):
        headers = await self._get_auth_headers(user_id)
        data = aiohttp.FormData()
        data.add_field('file', file_bytes, filename=file_name, content_type='application/pdf')

        async with self.session.post(f"{self.base_url}/resumes/upload", data=data, headers=headers) as response:
            if response.status in [200, 201]:
                result = await response.json()
                # Бэк возвращает словарь, вытаскиваем из него чистый UUID
                # Если в JSON ключ называется "resumeId", берем его
                resume_id = result.get("resumeId") 
                return resume_id
            return None

    # Функция старта интервью
    async def start_interview(self, telegram_id: int, resume_id: str):
        url = f"{self.base_url}/interviews/TEST/start"
        headers = await self._get_auth_headers(telegram_id)
        payload = {"resumeId": resume_id}
        
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f"DEBUG Start Interview Response: {data}")
                # Сверяемся со скриншотом: ключи interviewId и firstQuestion
                return {
                    "id": data.get("interviewId"),
                    "text": data.get("firstQuestion")
                }
            return None
        
    