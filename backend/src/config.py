from dotenv import load_dotenv
import os
from openai import AsyncOpenAI


load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT")

SECRET_AUTH = os.environ.get("SECRET_AUTH")
SECRET_USER_MANAGER = os.environ.get("SECRET_USER_MANAGER")

OPENAI_SECRET_API_KEY = os.environ.get("OPENAI_SECRET_API_KEY")

BOT_SECRET_TOKEN = os.environ.get("BOT_SECRET_TOKEN")

DATABASE_URL_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

client = AsyncOpenAI(
    base_url="https://api.proxyapi.ru/openai/v1", # адрес посредника
    api_key=OPENAI_SECRET_API_KEY,
)

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")

REDIS_URL_TGTOKEN = f"redis://{REDIS_HOST}:{REDIS_PORT}/1"
REDIS_URL_CACHE = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

BOT_NAME = os.environ.get("BOT_NAME")

GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")

MYMAIL = os.environ.get("MYMAIL")
