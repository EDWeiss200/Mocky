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

DATABASE_URL_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# client = AsyncOpenAI()