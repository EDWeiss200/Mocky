import asyncio
import logging
from config import config
from aiogram import Bot, Dispatcher
from handlers import router
from api_client import Backend_Client
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis


logging.basicConfig(level=logging.INFO)

async def main():
    storage = RedisStorage.from_url(config.REDIS_URL_FSM)

    redis_cookie = Redis.from_url(config.REDIS_URL_COOKIE, decode_responses = True)

    if await redis_cookie.ping():
        print('redis cookie connected')

    bot = Bot(token = config.BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    
    api = Backend_Client(base_url=config.BACKEND_URL, redis_client = redis_cookie)
    
    dp.include_router(router)

    print (f"Bot is running. Backend url: {config.BACKEND_URL}")
    try:
        await dp.start_polling(bot, api=api)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
    finally:
        print("session closing...")
        await api.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user")