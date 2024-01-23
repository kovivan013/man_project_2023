import asyncio
from functools import wraps
from typing import Any, Callable
from aiogram.types import Message, CallbackQuery

from pydantic import BaseModel, ValidationError
from man_project_2023.utils.debug import exceptions

from man_project_2023.telegram_bot.classes.api_requests import UserAPI

def check_super_admin(func: Callable):
    """
    Check admin permissions from list in settings
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper

def check_banned(func: Callable):
    """
    Check user is_banned status
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper

def catch_error(func: Callable):
    """
    Catch and report unexpected errors to logs and to user client
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except:
            from man_project_2023.telegram_bot.handlers.user_handlers import StartMH
            callback: CallbackQuery = args[1]
            state = kwargs["state"]
            if type(callback) == type(CallbackQuery()):
                await callback.answer(text=f"‼ Упс... Виникла несподівана помилка.\n",
                                      show_alert=True)
                await StartMH.start_menu(callback, state)

            print(f"Telegram bot error in func {func}")

    return wrapper





