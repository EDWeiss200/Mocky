class Backend_Client():

    def __init__(self, base_url):
        self.base_url = base_url

    async def send_message(self, user_id: int, text: str, interview_id : int):
        """Метод для отправки сообщения на бэкенд и получения ответа"""
        async with aiohttp.ClientSession() as session:
            payload = {"user_id": user_id, "interview_id":  interview_id, "text": text}
            
            # Делаем POST-запрос на эндпоинт /chat
            async with session.post(f"{self.base_url}/chat", json=payload) as response:
                # Ждем, пока бэкенд ответит и превращаем ответ в словарь (dict)
                result = await response.json()
                # Возвращаем только текст ответа от нейронки/бэкенда
                return result.get("answer", "Ошибка: Бэкенд не прислал ответ")

    async def link_account(self, user_id: int, code: str):
        """Метод для привязки кода с сайта к Telegram ID"""
        async with aiohttp.ClientSession() as session:
            payload = {"user_id": user_id, "code": code}
            
            async with session.post(f"{self.base_url}/auth/link", json=payload) as response:
                if response.status == 200:
                    return True
                return False