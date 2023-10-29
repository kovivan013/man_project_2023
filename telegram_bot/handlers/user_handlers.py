from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.types.input_media import InputMediaPhoto
from aiogram.dispatcher.storage import FSMContext
from man_project_2023.telegram_bot.states.states import ProfileStates, CurrentState, State
from man_project_2023.telegram_bot.utils.utils import HandlersUtils
from aiogram.dispatcher.filters import Text
from man_project_2023.telegram_bot.keyboards.keyboards import YesOrNo, Controls, MyProfile, Navigation, Filters, DropdownMenu
from man_project_2023.telegram_bot.classes.api_requests import UserAPI
from man_project_2023.telegram_bot.config import bot, Dispatcher


class ContextManager:

    message: Message = None
    usages_counter = False

    @classmethod
    async def send(cls, current_state: CurrentState,
                   required_state: State, image: str):
        photo = await current_state.state_photo(image=image)
        cls.message = await bot.send_photo(chat_id=current_state.state.chat,
                                           photo=photo,
                                           reply_markup=DropdownMenu.placeholder_menu(
                                               current_menu=await current_state.get_placeholder(
                                                   required_state=required_state
                                               )
                                           ))

    @classmethod
    async def select(cls):
        pass

    @classmethod
    async def edit(cls, current_state: CurrentState,
                   image: str):
        if cls.usages_counter:
            media = await current_state.state_photo(image=image)
            await cls.message.edit_media(media=InputMediaPhoto(
                media=media
            ),
            reply_markup=DropdownMenu.placeholder_menu(
                current_menu=await current_state.get_placeholder()
            ))
        cls.usages_counter = True

    @classmethod
    async def delete(cls):
        pass

    @classmethod
    async def reset_data(cls):
        cls.usages_counter = 0

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

    utils = HandlersUtils()
    context_manager1 = ContextManager()

    @classmethod
    async def context_manager(cls, message: Message, state: FSMContext) -> None:
        current_state = CurrentState(state,
                                     MyProfile,
                                     ProfileStates)
        await cls.context_manager1.send(current_state=current_state,
                                       required_state=ProfileStates.info_about,
                                       image="dashboard_profile")

        await ProfileStates.gigs.set()
        await cls.info_about(message=message,
                             state=state)


    @classmethod
    async def info_about(cls, message: Message, state: FSMContext) -> None:
        current_state = CurrentState(state,
                                     MyProfile,
                                     ProfileStates)
        await ProfileStates.info_about.set()
        # async with state.proxy() as data:
        #     callback_message: Message = data["context_manager"]
        # await current_state.context_manager(message=message,
        #                                     image="dashboard_profile")


        # await ProfileStates.info_about.set()
        # context_manager = await cls.utils.context_manager(current_state=current_state,
        #                                                   message=message,
        #                                                   image="dashboard_profile")



        # image = open('img/dashboard_profile.png', 'rb')
        # await bot.send_photo(chat_id=message.chat.id,
        #                      photo=await current_state.state_photo(image="dashboard_profile"),
        #                      reply_markup=DropdownMenu.placeholder_menu(
        #                          current_menu=await current_state.get_placeholder()
        #                      )
        #                      )
        # TODO: function menu
        await cls.context_manager1.edit(current_state=current_state,
                                        image="dashboard_profile")
        image = open('img/test35459468345687456.png', 'rb')
        # await bot.send_photo(chat_id=state.chat,
        #                      caption="text",
        #                      photo=image)

    @classmethod
    async def my_gigs(cls, message: Message, state: FSMContext) -> None:
        current_state = CurrentState(state,
                                     MyProfile)
        await ProfileStates.gigs.set()
        # async with state.proxy() as data:
        #     callback_message: Message = data["context_manager"]

        # image = open('img/dashboard_profile.png', 'rb')
        # await cls.utils.edit_context_manager(current_state=current_state,
        #                                      message=message)
        #
        # # TODO: function menu
        await cls.context_manager1.edit(current_state=current_state,
                                        image="dashboard_profile")
        image = open('img/test35459468345687456.png', 'rb')
        # await bot.send_photo(chat_id=state.chat,
        #                      caption="text",
        #                      photo=image)




class Test:

    utils = HandlersUtils()

    @classmethod
    async def keyboards_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
        current_state = CurrentState(state,
                                     MyProfile)
        image = open('img/test35459468345687456.png', 'rb')
        await callback.message.edit_media(media=InputMediaPhoto(
            media=image,
            caption=f"💻 *Оберіть необхідне меню:*",
            parse_mode="Markdown"
        ),
            reply_markup=DropdownMenu.menu_keyboard(
                buttons=await current_state.get_buttons()
            )
        )
        await ProfileStates.select_menu.set()

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
    dp.register_callback_query_handler(
        MyProfileMH.info_about, Text(equals=MyProfile().info_about_callback), state=ProfileStates.select_menu
    )
    dp.register_callback_query_handler(
        MyProfileMH.my_gigs, Text(equals=MyProfile().gigs_callback), state=ProfileStates.select_menu
    )
    dp.register_message_handler(
        MyProfileMH.context_manager, Text(equals="1"), state=["*"]
    )