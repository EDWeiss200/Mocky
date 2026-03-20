import asyncio
import logging
from config import BOT_TOKEN, BACKEND_URL
from aiogram import Bot, Dispatcher
from handlers import router
from api_client import Backend_Client

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token = BOT_TOKEN)
    dp = Dispatcher()
    
    api = Backend_Client(base_url=BACKEND_URL)
    dp.include_router(router)

    print (f"Bot is running. Backend url: {BACKEND_URL}")

    await dp.start_polling(bot, api=api)

if __name__ == "__main__":
    asyncio.run(main())