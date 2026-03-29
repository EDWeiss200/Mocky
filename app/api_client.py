import aiohttp

class Backend_Client():

    def __init__(self, base_url):
        self.base_url = base_url

    async def send_message(self, user_id: int, answerText: str, interview_id : int):
        """Метод для отправки сообщения на бэкенд и получения ответа"""
        async with aiohttp.ClientSession() as session:
            payload = {"answerText" : answerText}
            
            # Делаем POST-запрос на эндпоинт Answer Question
            async with session.post(f"{self.base_url}/interviews/answer/{interview_id}", json=payload) as response:
                result = await response.json()
                return result.get("answer", "Ошибка: Бэкенд не прислал ответ")

    # async def link_account(self, user_id: int, code: str):
    #     """Метод для привязки кода с сайта к Telegram ID"""
    #     async with aiohttp.ClientSession() as session:
    #         payload = {"user_id": user_id, "code": code}
            
    #         async with session.post(f"{self.base_url}/auth/link", json=payload) as response:
    #             if response.status == 200:
    #                 return True
    #             return False

    # Функция загрузки резюме, работает только после связки аккаунтов
    async def resume_upload(self, file_bytes : bytes, file_name : str):
        async with aiohttp.ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('file', file_bytes, filename=file_name)

                url = f"{self.base_url}/resumes/upload"
                async with session.post(url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                    return result.get("id") 
                return None

    # Функция старта интервью
    async def start_interview(self, resume_id: str):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/interviews/start"
            payload = {"resumeId": resume_id} # Как на твоем скриншоте
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                return None

    # Логин(создание нового акка в бд на основе тг акка)
    async def login(self, telegram_id: int, username: str):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/telegram/login"
            headers = {
                "x-bot-token" : "BOT_SECRET_TOKEN",
                "ContentType" : "application/json"
            }
            payload = {
                "telegram_id" : telegram_id,
                "username" : username
            }
            
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return None
