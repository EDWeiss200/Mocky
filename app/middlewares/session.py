import time
import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

class SessionUpdateMiddleware(BaseMiddleware):
    def __init__(self, refresh_cooldown: int = 300):
        """
        :param refresh_cooldown: Кулдаун в секундах (по умолчанию 300 сек = 5 минут)
        """
        super().__init__()
        self.refresh_cooldown = refresh_cooldown
        self._last_refresh: Dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)

        user_id = event.from_user.id
        api = data.get("api")
        
        if api:
            current_time = time.time()
            last_time = self._last_refresh.get(user_id, 0.0)

            if current_time - last_time > self.refresh_cooldown:
                try:
                    username = event.from_user.username or event.from_user.first_name or "Unknown"
                    
                    await api.refresh_session(user_id, username)
                    
                    self._last_refresh[user_id] = current_time
                except Exception as e:
                    logging.error(f"Ошибка обновления сессии для юзера {user_id}: {e}")

        return await handler(event, data)