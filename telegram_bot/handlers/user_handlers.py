from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.types.input_media import InputMediaPhoto
from aiogram.dispatcher.storage import FSMContext
from man_project_2023.telegram_bot.states.states import ProfileStates, CurrentState
from aiogram.dispatcher.filters import Text
from man_project_2023.telegram_bot.utils.utils import StateUtils
from man_project_2023.telegram_bot.keyboards.keyboards import YesOrNo, Controls, MyProfile, Navigation, Filters, DropdownMenu
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


class Test(StateUtils):

    @classmethod
    async def keyboards_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
        current_state = CurrentState(state,
                                     MyProfile)
        image = open('img/test35459468345687456.png', 'rb')
        await callback.message.edit_media(media=InputMediaPhoto(
            media=image,
            caption=f"*Оберіть необхідне меню* 💻*:*",
            parse_mode="Markdown"
        ),
            reply_markup=DropdownMenu.menu_keyboard(
                buttons=await current_state.get_buttons()
            )
        )

        # reply_markup = DropdownMenu.menu_keyboard(
        #     state=state_name,
        #     buttons=MyProfile().get_buttons()
        # )

    @classmethod
    async def input_kb_func(cls, message: Message, state: FSMContext) -> None:
        current_state = CurrentState(state,
                                     MyProfile)

        image = open('img/dashboard_profile.png', 'rb')
        await ProfileStates.gigs.set()
        await bot.send_photo(chat_id=message.chat.id,
                             photo=image,
                             caption="Test input message to keyboards select menu",
                             reply_markup=DropdownMenu.placeholder_menu(
                                 current_menu=await current_state.get_placeholder()
                             )
                             )
        image = open('img/test35459468345687456.png', 'rb')
        await message.answer_photo(caption=f"Test caption",
                                   photo=image
                                   )

class UserProfileMH:
    pass

def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        StartMH.cls_menu, commands=["start"], state=None
    )
    dp.register_message_handler(
        MyProfileMH.info_about, commands=["profile"], state=None
    )
    dp.register_message_handler(
        Test.input_kb_func, commands=["test"], state=None
    )
    dp.register_callback_query_handler(
        Test.keyboards_menu, Text(equals="placeholder_callback"), state=["*"]
    )