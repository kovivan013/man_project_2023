import asyncio
from functools import wraps
from typing import Any
from aiogram.types import Message
from man_project_2023.telegram_bot.classes.api_requests import UserAPI


# def check_status(func=None, /, *, user_status=None):
#
#     @wraps(func)
#     async def wrapper(*args, **kwargs) -> Any:
#
#         message: Message = args[1]
#         telegram_id: int = message.from_user.id
#         status = await UserAPI.get_user_status(telegram_id=telegram_id)
#
#         if status == user_status:
#             await func(*args, kwargs)
#
#     return wrapper

# def check_status(user_status):
#     def decorator(func):
#
#         @wraps(func)
#         async def wrapper(cls, *args, **kwargs):
#             print(args, "||||||||", kwargs)
#             # message: Message = args[1]
#             telegram_id: int = 1125858430
#             status = await UserAPI.get_user_status(telegram_id=telegram_id)
#
#             if status == user_status:
#                 await func(cls, *args, kwargs)
#
#         return wrapper
#     return decorator

def check_status(user_status):
    def decorator(func):
        @wraps(func)
        async def wrapper(cls, *args, **kwargs):
            # message: Message = args[1]
            telegram_id: int = 1125858430
            status = await UserAPI.get_user_status(telegram_id=telegram_id)

            if status == user_status:
                await func(*args, kwargs)

        return wrapper
    return decorator


