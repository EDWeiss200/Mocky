from config import config
import aiohttp
import logging
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


    async def login(self, telegram_id: int, username: str):
        url = f"{self.base_url}/telegram/login"
        
        headers = {
            "x-bot-token": config.BOT_SECRET_TOKEN, 
            "Content-Type": "application/json"
        }
        payload = {"telegram_id": str(telegram_id), "username": username}
        
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status in [200, 204]:
                set_cookie = response.headers.get("Set-Cookie")
                if set_cookie:
                    clean_cookie = set_cookie.split(';')[0]
                    await self.redis.set(f"auth_sid:{telegram_id}", clean_cookie, ex=86400)
                return True
            logging.error(f"Ошибка логина {response.status}: {await response.text()}")
            return False


    async def refresh_session(self, telegram_id: int, username: str = "User"):
        """Продлевает жизнь куки в Redis или делает тихий логин, если она пропала."""
        key = f"auth_sid:{telegram_id}" 
        
        try:
            exists = await self.redis.exists(key)
            
            if exists:
                await self.redis.expire(key, 86400)
            else:
                await self.login(telegram_id, username)
                
        except Exception as e:
            logging.error(f"Ошибка при обновлении сессии для {telegram_id}: {e}")


    async def confirm_link(self, telegram_id: int, token: str):
        url = f"{self.base_url}/telegram/link/confirm"
        
        headers = {
            "x-bot-token": config.BOT_SECRET_TOKEN,
            "Content-Type": "application/json"
        }
        
        payload = {
            "telegram_id": str(telegram_id),
            "token": token
        }

        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status in [200, 204]:
                set_cookie = response.headers.get("Set-Cookie")
                if set_cookie:
                    clean_cookie = set_cookie.split(';')[0]
                    await self.redis.set(f"auth_sid:{telegram_id}", clean_cookie, ex=86400)
                return True
            print(f"Ошибка связки: {response.status}")
            return False


    async def resume_upload(self, user_id: int, file_bytes: bytes, file_name: str):
        headers = await self._get_auth_headers(user_id)
        data = aiohttp.FormData()
        data.add_field('file', file_bytes, filename=file_name, content_type='application/pdf')

        async with self.session.post(f"{self.base_url}/resumes/upload", data=data, headers=headers) as response:
            if response.status in [200, 201]:
                result = await response.json()
                resume_id = result.get("resumeId") 
                return resume_id
            if response.status == 402:
                return {"error": "payment_required"}
            return None

    
    async def answer_voice(self, user_id: int, file_bytes: bytes, file_name: str, interview_id: str):
        headers = await self._get_auth_headers(user_id)
        data = aiohttp.FormData()
        data.add_field('file', file_bytes, filename=file_name, content_type='audio/mpeg')
        url = f'{self.base_url}/interviews/answer/voice/{interview_id}'
        async with self.session.post(url, data=data, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return None
            

    async def start_interview(self, telegram_id: int, resume_id: str, number_questions: int = 5, role: str = "pragmatic_lead"):
        url = f"{self.base_url}/interviews/start"
        headers = await self._get_auth_headers(telegram_id)
        payload = {
            "resumeId": resume_id,
            "numberQuestion": number_questions,
            "role": role
        }
        
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "id": data.get("interviewId"),
                    "text": data.get("firstQuestion")
                }
            if response.status == 402:
                return {"error": "payment_required"}
            return None
        

    async def send_message(self, user_id: int, answerText: str, interview_id: str):
        url = f"{self.base_url}/interviews/answer/{interview_id}"
        payload = {"answerText": answerText}
        headers = await self._get_auth_headers(user_id) 
        
        async with self.session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                return await response.json() 
            if response.status == 402:
                return {"error": "payment_required"}
            return None
                        

    async def finish_interview(self, telegram_id: int, interview_id: str):
        url = f"{self.base_url}/interviews/finish/{interview_id}"
        headers = await self._get_auth_headers(telegram_id)
        
        async with self.session.post(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "status": data.get("status"),
                    "totalScore": data.get("total_score", 0),
                    "feedback": data.get("feedback", "Анализ не сформирован")
                }
            logging.error(f"Ошибка API finish: {response.status}")
            return False
        
        
    async def get_active_interviews(self, telegram_id: int):
        """Получить список активных интервью (Эндпоинт /interviews/active)"""
        url = f"{self.base_url}/interviews/active"
        headers = await self._get_auth_headers(telegram_id)
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return []

    async def get_resumes(self, telegram_id: int):
            """Эндпоинт GET /resumes"""
            url = f"{self.base_url}/resumes"
            headers = await self._get_auth_headers(telegram_id)
            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                return []

    async def get_interview_history(self, telegram_id: int, interview_id: str):
        """Эндпоинт GET /messages/{interview_id}/history"""
        url = f"{self.base_url}/messages/{interview_id}/history"
        headers = await self._get_auth_headers(telegram_id)
        async with self.session.get(url, headers=headers) as resp:
            if resp.status == 200:
                return await resp.json()
            return []

    async def get_completed_interview_details(self, telegram_id: int):
        url = f"{self.base_url}/interviews/completed"
        headers = await self._get_auth_headers(telegram_id)
        
        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            return []

    async def analyze_resume(self, telegram_id: int, resume_id: str):
        url = f"{self.base_url}/resumes/{resume_id}/analyze"
        headers = await self._get_auth_headers(telegram_id)
        
        async with self.session.post(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            if response.status == 402:
                return {"error": "payment_required"}
            return None

    async def delete_resume(self, telegram_id: int, resume_id: str):
        url = f"{self.base_url}/resumes/{resume_id}"
        headers = await self._get_auth_headers(telegram_id)
        
        async with self.session.delete(url, headers=headers) as response:
            return response.status in [200, 204]

    async def delete_interview(self, telegram_id: int, interview_id: str):
        url = f"{self.base_url}/interviews/{interview_id}"
        headers = await self._get_auth_headers(telegram_id)
        
        async with self.session.delete(url, headers=headers) as response:
            return response.status in [200, 204]