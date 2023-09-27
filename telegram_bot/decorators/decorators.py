from functools import wraps
from typing import Any
from aiogram.types import Message
from man_project_2023.telegram_bot.classes.api_requests import UserAPI


def check_status(func):

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        message: Message = args[1]
        telegram_id: int = message.from_user.id
        status = await UserAPI.get_user_status(telegram_id=telegram_id)
        if status == 0 and func.__name__ == "lost_things_menu":
            await func(*args, **kwargs)
        elif status == 1 and func.__name__ == "search_things_menu":
            await func(*args, **kwargs)
    return wrapper