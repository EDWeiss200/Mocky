import os
from dotenv import load_dotenv

load_dotenv()

class Config():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BACKEND_URL= os.getenv("BACKEND_URL")
    BOT_SECRET_TOKEN = os.getenv("BOT_SECRET_TOKEN")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "6379")

    REDIS_URL_FSM = f'redis://{REDIS_HOST}:{REDIS_PORT}/2'
    REDIS_URL_COOKIE = f'redis://{REDIS_HOST}:{REDIS_PORT}/3'

config = Config()