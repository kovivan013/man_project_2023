from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from man_project_2023.telegram_bot.states.states import ProfileStates
from aiogram.dispatcher.filters import Text
from man_project_2023.telegram_bot.keyboards.keyboards import YesOrNo, Controls, FinderMenu, SeekerMenu
from man_project_2023.telegram_bot.classes.api_requests import UserAPI
from man_project_2023.telegram_bot.config import bot, Dispatcher

class RegisterMH:
    pass

class FinderMH: # Тот кто ищет (НАШЕЛ)

    @classmethod
    async def cls_menu(cls, message: Message) -> None:
        await message.answer(text=f"Меню детектива",
                             reply_markup=FinderMenu.keyboard())


class SeekerMH: # Тот кто ищет (ПОТЕРЯЛ)

    @classmethod
    async def cls_menu(cls, message: Message) -> None:
        await message.answer(text=f"Меню поиска",
                             reply_markup=FinderMenu.keyboard())


class StartMH:

    finder = FinderMH()
    seeker = SeekerMH()

    @classmethod
    async def cls_menu(cls, message: Message) -> None:
        user_status = await UserAPI.get_user_status(telegram_id=message.from_user.id)
        if user_status:
            await cls.finder.menu(message)
        else:
            await cls.seeker.menu(message)

class MyProfileMH:

    @classmethod
    async def cls_menu(cls, message: Message, state: FSMContext) -> None:
        pass


class UserProfileMH:
    pass


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        StartMH.cls_menu, commands=["start"], state=None
    )