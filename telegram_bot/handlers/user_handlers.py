from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text
from man_project_2023.telegram_bot.decorators.decorators import check_status
from man_project_2023.telegram_bot.config import Dispatcher

class StartMH:

    @classmethod
    async def menu(cls, message: Message) -> None:
        await cls.search_things_menu(message)
        await cls.lost_things_menu(message)

    @classmethod
    @check_status
    async def search_things_menu(cls, message: Message) -> None:
        await message.answer(text=f"Меню детектива")

    @classmethod
    @check_status
    async def lost_things_menu(cls, message: Message) -> None:
        await message.answer(text=f"Меню поиска")


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        StartMH.menu, commands=["start"], state=None
    )