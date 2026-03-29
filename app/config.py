import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL= os.getenv("BACKEND_URL")
BOT_SECRET_TOKEN = os.getenv("BOT_SECRET_TOKEN")