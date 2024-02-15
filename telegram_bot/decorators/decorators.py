import asyncio
from functools import wraps
from typing import Any, Callable, Union
from aiogram.types import Message, CallbackQuery

from pydantic import BaseModel, ValidationError
from utils.debug import exceptions

from telegram_bot.classes.api_requests import UserAPI
from telegram_bot.classes.utils_classes import Storage, FSMContext

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
        # try:
            return await func(*args, **kwargs)
        # except Exception as err:
            from man_project_2023.telegram_bot.handlers.user_handlers import StartMH
            callback: CallbackQuery = args[1]
            state = kwargs["state"]
            if type(callback) == type(CallbackQuery()):
                await callback.answer(text=f"‼ Упс... Виникла несподівана помилка.\n",
                                      show_alert=True)
                await StartMH.start_menu(callback, state)
            print(f"Telegram bot error in func {func}\n"
                  f"Exception: {err}")

    return wrapper

class HistoryManager(Storage):

    _KEY = "history_manager"

    def __init__(self, history: dict = {}):
        self.history = history

    def register(self, group: Union[str, list], onetime: bool = False):
        def wrapper(func: Callable, _state: FSMContext = None) -> Callable:
            @wraps(func)
            async def wrap(*args, **kwargs) -> Any:
                state: FSMContext = _state if _state else kwargs["state"]
                storage: self = await self._storage(state)
                if not isinstance(instance := group, list):
                    instance = [group]
                await func(*args, **kwargs)
                for i in instance:
                    try:
                        data: dict = storage.history.setdefault(i, {"history": {}})
                        last_index = max(data["history"], default=0) + 1
                        if onetime and last_index > 1:
                            last_index -= 1
                            value = data["history"][last_index]
                            data["history"] = {1: value}
                        data["onetime"] = onetime
                        data["history"].update({
                            last_index: {
                                "func": func,
                                "args": args,
                                "kwargs": kwargs
                            }
                        })
                        storage.history[i].update(data)
                    except Exception as err:
                        print(f"ERROR in {self.register}: ", err)
                await self._save(state, storage)
            return wrap
        return wrapper

    def __call__(self, group: str, onetime: bool = False):
        def wrapper(func: Callable) -> Callable:
            @wraps(func)
            async def wrap(*args, **kwargs) -> Any:
                return await self.register(group=group,
                                           onetime=onetime)(func)(*args, **kwargs)
            return wrap
        return wrapper

    async def back(self, state: FSMContext, group: str):
        storage: self = await self._storage(state)
        if last_index := max((data := storage.history.get(group, {})).get("history", {}), default=0):
            try:
                func, args, kwargs = tuple(data["history"][last_index].values())
                kwargs["state"] = state
                onetime = data["onetime"]
                await self.register(group=group,
                                    onetime=onetime)(func, state)(*args, **kwargs)
                if not onetime and last_index > 1:
                    storage.history[group]["history"].pop(last_index)
            except Exception as err:
                print(f"ERROR in {self.back}: {err}\nOriginal function: {func.__name__}\n{func}")
            await self._save(state, storage)
        return None

    # def back(self, group: str):
    #         async def wrapper(*args, **kwargs):
    #             state = await func(*args, **kwargs)
    #             return await self.backward(state=state,
    #                                        group=group)
    #         return wrapper




history_manager = HistoryManager()















