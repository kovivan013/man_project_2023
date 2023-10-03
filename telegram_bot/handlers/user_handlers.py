from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from man_project_2023.telegram_bot.states.states import ProfileStates
from aiogram.dispatcher.filters import Text
from man_project_2023.telegram_bot.keyboards.keyboards import YesOrNo, Controls, FinderMenu, SeekerMenu, MyProfile, Navigation, Filters
from man_project_2023.telegram_bot.classes.api_requests import UserAPI
from man_project_2023.telegram_bot.config import bot, Dispatcher

class RegisterMH:
    pass

class FinderMH: # Тот кто ищет (НАШЕЛ)

    @classmethod
    async def cls_menu(cls, message: Message) -> None:
        photo = open("img/dtpanel.png", "rb")
        # img = open("img/dashboard_profile.png", "rb")
        # bg = open("img/bg.png", "rb")
        # await bot.send_photo(chat_id=message.from_user.id,
        #                      photo=bg,
        #                      reply_markup=Filters.dashboard_filter(),
        #                      parse_mode="Markdown")
        await bot.send_photo(chat_id=message.from_user.id,
                             photo=photo,
                             caption="Знайдено речей за Вересень: *16*",
                             parse_mode="Markdown",
                             reply_markup=Filters.dashboard_filter())
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"Немає доступних оголошень",
                               reply_markup=Navigation.finder_keyboard())



class SeekerMH: # Тот кто ищет (ПОТЕРЯЛ)

    @classmethod
    async def cls_menu(cls, message: Message) -> None:
        await message.answer(text=f"Меню поиска")


class StartMH:

    finder = FinderMH()
    seeker = SeekerMH()

    @classmethod
    async def cls_menu(cls, message: Message) -> None:
        user_status = await UserAPI.get_user_mode(telegram_id=message.from_user.id)
        if user_status:
            await cls.finder.cls_menu(message)
        else:
            await cls.seeker.cls_menu(message)

class MyProfileMH:

    @classmethod
    async def cls_menu(cls, message: Message, state: FSMContext) -> None:

        photo = open('img/mode_1_main_menu.png', 'rb')
        await bot.send_photo(chat_id=message.chat.id,
                             photo=photo,
                             reply_markup=MyProfile.keyboard())

class UserProfileMH:
    pass


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        StartMH.cls_menu, commands=["start"], state=None
    )
    dp.register_message_handler(
        MyProfileMH.cls_menu, commands=["profile"], state=None
    )