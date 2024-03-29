import asyncio
from functools import wraps
from config import bot, settings
from typing import Any, Callable, Union
from aiogram.types import Message, CallbackQuery

from pydantic import BaseModel, ValidationError
from classes.api_requests import UserAPI
from keyboards.keyboards import MainMenu
from classes.utils_classes import Storage, FSMContext, filters_manager

def check_super_admin(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        state: FSMContext = kwargs["state"]
        telegram_id: int = state.user
        if telegram_id in settings.ADMINS:
            return await func(*args, **kwargs)

    return wrapper

def check_banned(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)

    return wrapper

def check_registered(func: Callable) -> Callable:

    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        state: FSMContext = kwargs["state"]
        response = await UserAPI.get_user(telegram_id=state.user)
        if response._success:
            return await func(*args, **kwargs)
        else:
            from handlers.user_handlers import RegisterMH
            return await RegisterMH.start_register(*args[1:], **kwargs)

    return wrapper

def private_message(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        state: FSMContext = kwargs["state"]
        if state.chat == state.user:
            return await func(*args, **kwargs)
        else:
            await bot.send_message(chat_id=state.chat,
                                   text=f"❌ *FindIt Bot поки що не доступний у групових чатах!*",
                                   reply_markup=MainMenu.link_keyboard(),
                                   parse_mode="Markdown")
    return wrapper

def reset_filters(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        state = kwargs["state"]
        await filters_manager.reset_filters(state)
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
        except Exception as err:
            from handlers.user_handlers import StartMH
            from classes.utils_classes import context_manager
            callback: CallbackQuery = args[1]
            state = kwargs["state"]
            if type(callback) == type(CallbackQuery()):
                await callback.answer(text=f"‼ Упс... Виникла несподівана помилка.\n",
                                      show_alert=True)
                await context_manager.delete(state)
                await StartMH.start_menu(callback,
                                         state=state)
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
        else:
            await self.back(state=state,
                            group="main_menu")
        return None

history_manager = HistoryManager()















