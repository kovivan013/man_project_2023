import asyncio
from functools import wraps
from typing import Any, Callable
from aiogram.types import Message
from man_project_2023.telegram_bot.classes.api_requests import UserAPI

def check_finder_mode(func: Callable) -> Callable:

    @wraps(func)
    async def wrapper(*args, **kwargs):
        pass
    return wrapper