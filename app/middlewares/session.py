import time
import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from redis.asyncio import Redis

class SessionUpdateMiddleware(BaseMiddleware):
    async def __call__(
            
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, (Message, CallbackQuery)):
            return await handler(event, data)
        
        user_id = event.from_user.id
        api = data.get("api")
        username = event.from_user.username or event.from_user.first_name or "Unknown"
    
        last_refresh = await api.redis.get(f"last_refresh:{user_id}")
        if last_refresh is None:
            await api.refresh_session(user_id, username)
            await api.redis.set(f"last_refresh:{user_id}", "1", ex=3600)

        return await handler(event, data)