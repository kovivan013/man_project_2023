import asyncio
from functools import wraps
from typing import Any, Callable
from aiogram.types import Message

from pydantic import BaseModel, ValidationError
from man_project_2023.utils.debug import exceptions

from man_project_2023.telegram_bot.classes.api_requests import UserAPI

def validate_request(model: BaseModel):
    def decorator(func: Callable) -> Callable:

        @wraps(func)
        async def wrapper(*args, **kwargs):
            print(args, kwargs)
            try:
                model.model_validate(kwargs)
                print(1)
                return func(*args, **kwargs)
            except ValidationError:
                raise exceptions.InvalidInputData


        return wrapper
    return decorator