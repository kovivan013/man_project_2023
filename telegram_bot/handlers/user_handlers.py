from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from man_project_2023.telegram_bot.states.states import ProfileStates
from aiogram.dispatcher.filters import Text
from man_project_2023.telegram_bot.keyboards.keyboards import YesOrNo, Controls, MyProfile, Navigation, Filters, MainMenu, DropdownMenu
from man_project_2023.telegram_bot.classes.api_requests import UserAPI
from man_project_2023.telegram_bot.config import bot, Dispatcher


class RegisterMH:
    pass

class FinderMH: # Тот кто ищет (НАШЕЛ)

    @classmethod
    async def cls_menu(cls, message: Message) -> None:
        photo = open("img/dtpanel1.png", "rb")
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
        photo = open("img/marketplace_png.png", "rb")
        await bot.send_photo(chat_id=message.from_user.id,
                             caption=f"💡 Що шукаєш сьогодні?",
                             photo=photo,
                             reply_markup=MainMenu.seeker_keyboard())



class StartMH:

    finder = FinderMH()
    seeker = SeekerMH()

    @classmethod
    async def cls_menu(cls, message: Message) -> None:
        data: dict = {
            "telegram_id": message.from_user.id,
            "username": message.from_user.username if message.from_user.username is not None else ""
        }
        await UserAPI.create_user(**data)
        user_status = await UserAPI.get_user_mode(telegram_id=message.from_user.id)
        if user_status:
            await cls.finder.cls_menu(message)
        else:
            await cls.seeker.cls_menu(message)

class MyProfileMH:

    @classmethod
    async def info_about(cls, message: Message, state: FSMContext) -> None:
        await ProfileStates.info_about.set()
        image = open('img/dashboard_profile.png', 'rb')
        await bot.send_photo(chat_id=message.chat.id,
                             photo=image,
                             reply_markup=MyProfile.info_about_keyboard())

    @classmethod
    async def my_gigs(cls, callback: CallbackQuery, state: FSMContext) -> None:
        pass

    @classmethod
    async def dropdown_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
        image = open('img/dashboard_profile.png', 'rb')
        await callback.message.edit_reply_markup(reply_markup=DropdownMenu.menu_keyboard(state=await state.get_state(), buttons=dict(MyProfile.get_keyboard())["inline_keyboard"]))

class UserProfileMH:
    pass


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        StartMH.cls_menu, commands=["start"], state=None
    )
    dp.register_message_handler(
        MyProfileMH.info_about, commands=["profile"], state=None
    )
    dp.register_callback_query_handler(
        MyProfileMH.dropdown_menu, Text(equals=MyProfile.placeholder_callback), state=ProfileStates.info_about
    )