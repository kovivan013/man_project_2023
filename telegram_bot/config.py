import os

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

class Settings(BaseSettings):
    # "http://bot_api:8008"
    BASE_API_URL: str = "http://127.0.0.1:8008"
    ADMINS: list = [1125858430, 1067582521, 1055676461]
    HELPERS_CHAT: int = -4186817944


settings = Settings()
load_dotenv()

BASE_API_URL: str = settings.BASE_API_URL
admins_list: list = settings.ADMINS
helpers_chat: int = settings.HELPERS_CHAT


storage = MemoryStorage()
API_TOKEN: str = os.getenv("TELEBOT_TOKEN")
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot=bot,
                storage=storage)

