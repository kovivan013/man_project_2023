import asyncio
from functools import wraps
from typing import Any, Callable
from aiogram.types import Message

from pydantic import BaseModel, ValidationError
from man_project_2023.utils.debug import exceptions

from man_project_2023.telegram_bot.classes.api_requests import UserAPI

def sync(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    return wrapper

