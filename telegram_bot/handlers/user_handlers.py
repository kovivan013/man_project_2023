from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters import Text
from man_project_2023.telegram_bot.decorators.decorators import check_status
from man_project_2023.telegram_bot.config import Dispatcher

class RegisterMH:
    pass

class FinderMH: # Тот кто ищет (НАШЕЛ)

    @classmethod
    @check_status(1)
    async def menu(cls, message: Message) -> None:
        print(f"Меню детектива")


class SeekerMH: # Тот кто ищет (ПОТЕРЯЛ)

    @classmethod
    @check_status(0)
    async def menu(cls, message: Message) -> None:
        print(f"Меню поиска")


class StartMH:
    finder = FinderMH()
    seeker = SeekerMH()

    @classmethod
    async def menu(cls, message: Message) -> None:
        await cls.seeker.menu(message)
        await cls.finder.menu(message)


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        StartMH.menu, commands=["start"], state=None
    )