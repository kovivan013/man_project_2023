import os

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

class Settings(BaseSettings):
    _BASE_API_URL: str = "http://127.0.0.1:8000"

settings = Settings()
load_dotenv()

BASE_API_URL: str = settings._BASE_API_URL

storage = MemoryStorage()
API_TOKEN: str = os.getenv("TELEBOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot,
                storage=storage)
