import datetime

import aiogram.types
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.types.input_media import InputMediaPhoto, InputFile

from aiogram.dispatcher.storage import FSMContext
from man_project_2023.telegram_bot.states.states import ProfileStates, CurrentState, State
from man_project_2023.telegram_bot.utils.utils import HandlersUtils
from aiogram.dispatcher.filters import Text
from man_project_2023.telegram_bot.keyboards.keyboards import (
    YesOrNo, Controls, MyProfile, Navigation, Filters, DropdownMenu, UpdateProfile,
    InlineKeyboardMarkup
)
from man_project_2023.telegram_bot.classes.api_requests import UserAPI
from man_project_2023.telegram_bot.config import bot, Dispatcher



class ContextManager:


    def __init__(self):
        self.current_state: CurrentState = None
        self.message: Message = None
        self.messages_to_delete: list[Message] = []
        self.previous_state: str = None
        self.is_used = False

    async def send(self, current_state: CurrentState,
                   required_state: State, image: str):
        self.current_state = current_state
        photo = await self.current_state.state_photo(image=image)
        self.message = await bot.send_photo(chat_id=self.current_state.state.chat,
                                            photo=photo,
                                            reply_markup=DropdownMenu.placeholder_menu(
                                               current_menu=await self.current_state.get_placeholder(
                                                   required_state=required_state
                                               )
                                           ))


    async def select(self, current_state: CurrentState = None,
                     delete_messages: bool = False,
                     reply_markup: InlineKeyboardMarkup = None):
        if current_state is not None:
            self.current_state = current_state
        if delete_messages:
            await self.delete_context_messages()

        await self.set_previous_state()
        image = open('img/test35459468345687456.png', 'rb')
        await self.message.edit_media(media=InputMediaPhoto(
            media=image,
            caption=f"💻 *Оберіть необхідне меню:*",
            parse_mode="Markdown"
        ),
            reply_markup=DropdownMenu.menu_keyboard(
                buttons=await self.current_state.get_buttons(reply_markup=reply_markup)
        ))


    async def edit(self, text: str = None,
                   image: str = None,
                   reply_markup: InlineKeyboardMarkup = None,
                   with_placeholder: bool = True):
        if self.is_used:

            if not await self.states_equals():
                await self.delete_context_messages()

            media = await self.current_state.state_photo(image=image)
            await self.message.edit_media(media=InputMediaPhoto(
                media=media,
                caption=text,
                parse_mode="Markdown"
            ),
                reply_markup=DropdownMenu.placeholder_menu(
                    current_menu=await self.current_state.get_placeholder()
                ) if reply_markup is None else reply_markup)
        self.is_used = True


    async def appent_delete_list(self, message: Message):
        self.messages_to_delete.append(message.message_id)


    async def delete_context_messages(self):
        for message_id in self.messages_to_delete:
            await bot.delete_message(chat_id=self.current_state.state.chat,
                                     message_id=message_id)
        self.messages_to_delete.clear()


    async def set_previous_state(self):
        self.previous_state = await self.current_state.get_name()


    async def states_equals(self) -> bool:
        return self.previous_state == await self.current_state.get_name()


    async def delete(self):
        await self.message.delete()
        self.reset_data()


    def reset_data(self):
        self.is_used = False



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
    __context_manager = ContextManager()

    @classmethod
    async def select_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
        current_state = CurrentState(state=state,
                                     keyboard_class=MyProfile,
                                     state_class=ProfileStates)

        await cls.__context_manager.select()
        await ProfileStates.select_menu.set()

    @classmethod
    async def context_manager(cls, message: Message, state: FSMContext) -> None:
        current_state = CurrentState(state=state,
                                     keyboard_class=MyProfile,
                                     state_class=ProfileStates)

        await cls.__context_manager.send(current_state=current_state,
                                         required_state=ProfileStates.info_about,
                                         image="dashboard_profile")
        await cls.info_about(message=message,
                             state=state)


    @classmethod
    async def info_about(cls, message: Message, state: FSMContext) -> None:
        current_state = CurrentState(state=state,
                                     keyboard_class=MyProfile,
                                     state_class=ProfileStates)

        await ProfileStates.info_about.set()
        await cls.__context_manager.edit(image="dashboard_profile")
        image = open('img/reg_data_board.png', 'rb')

        if not await cls.__context_manager.states_equals():
            await cls.__context_manager.appent_delete_list(
                await bot.send_photo(chat_id=state.chat,
                                     caption="📃 *Опис*"
                                             "\n\n"
                                             "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed ornare massa sapien, a feugiat nisi dignissim in. Integer non est dignissim, vehicula odio eget."
                                             "\n\n"
                                             "⭐ *Досягнення*"
                                             "\n\n"
                                             "Недоступно",
                                     photo=image,
                                     parse_mode="Markdown",
                                     reply_markup=MyProfile.info_about_keyboard())
            )



    @classmethod
    async def my_gigs(cls, message: Message, state: FSMContext) -> None:
        current_state = CurrentState(state=state,
                                     keyboard_class=MyProfile,
                                     state_class=ProfileStates)
        await ProfileStates.gigs.set()
        await cls.__context_manager.edit(image="dashboard_profile")
        if not await cls.__context_manager.states_equals():
            preview = open('img/423.png', 'rb')
            await cls.__context_manager.appent_delete_list(
                await bot.send_photo(chat_id=state.chat,
                                     caption="Я знайшов *чорну куртку*.\n"
                                             "📍 *Кременчук*\n"
                                             "⌚ *Сьогодні, об 16:56*",
                                     photo=preview,
                                     reply_markup={"inline_keyboard": [[{"text": "⚙  Налаштування️", "callback_data": "3754t6"}]]},
                                     parse_mode="Markdown")
            )
            preview = open('img/sh.png', 'rb')
            await cls.__context_manager.appent_delete_list(
                await bot.send_photo(chat_id=state.chat,
                                     caption="Я знайшов *шапку*.\n"
                                             "📍 *Кременчук*\n"
                                             "⌚ *Учора, об 11:32*",
                                     photo=preview,
                                     reply_markup={
                                         "inline_keyboard": [[{"text": "⚙  Налаштування️", "callback_data": "3754t6"}]]},
                                     parse_mode="Markdown")
            )
            preview = open('img/pas.png', 'rb')
            await cls.__context_manager.appent_delete_list(
                await bot.send_photo(chat_id=state.chat,
                                     caption="Я знайшов *паспорт на ім'я* \*\*\*\*\*\* \*\*\*\*\*\*\*\*\*\*.\n"
                                             "📍 *Кременчук*\n"
                                             "⌚ *25.10.23*",
                                     photo=preview,
                                     reply_markup={
                                         "inline_keyboard": [[{"text": "⚙  Налаштування️", "callback_data": "3754t6"}],
                                                             [{"text": "Додати оголошення ➕", "callback_data": "375423t6"}]]},
                                     parse_mode="Markdown")
            )


    @classmethod
    async def edit_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
        current_state = CurrentState(state=state,
                                     keyboard_class=UpdateProfile,
                                     state_class=ProfileStates)
        await cls.__context_manager.select(current_state=current_state,
                                           delete_messages=True,
                                           reply_markup=UpdateProfile.keyboard())

    @classmethod
    async def edit_username(cls, callback: CallbackQuery, state: FSMContext) -> None:
        current_state = CurrentState(state=state,
                                     keyboard_class=UpdateProfile,
                                     state_class=ProfileStates)
        await ProfileStates.username.set()
        await cls.__context_manager.edit(text="⌨️ *Уведіть Ваш новий нікнейм:*",
                                         image="dashboard_profile",
                                         reply_markup=UpdateProfile.base_keyboard(),
                                         with_placeholder=False)

# class Test:
#
#     utils = HandlersUtils()
#
#     @classmethod
#     async def keyboards_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
#         current_state = CurrentState(state,
#                                      MyProfile)
#         image = open('img/test35459468345687456.png', 'rb')
#         await callback.message.edit_media(media=InputMediaPhoto(
#             media=image,
#             caption=f"💻 *Оберіть необхідне меню:*",
#             parse_mode="Markdown"
#         ),
#             reply_markup=DropdownMenu.menu_keyboard(
#                 buttons=await current_state.get_buttons()
#             )
#         )
#         await ProfileStates.select_menu.set()
#
#     @classmethod
#     async def input_kb_func(cls, message: Message, state: FSMContext) -> None:
#         current_state = CurrentState(state,
#                                      MyProfile)
#
#
#         image = open('img/dashboard_profile.png', 'rb')
#         await ProfileStates.gigs.set()
#         await bot.send_photo(chat_id=message.chat.id,
#                              photo=image,
#                              caption="Test input message to keyboards select menu",
#                              reply_markup=DropdownMenu.placeholder_menu(
#                                  current_menu=await current_state.get_placeholder()
#                              )
#                              )
#         image = open('img/test35459468345687456.png', 'rb')
#         await message.answer_photo(caption=f"Test caption",
#                                    photo=image
#                                    )

class UserProfileMH:
    pass

def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        StartMH.cls_menu, commands=["start"], state=None
    )
    dp.register_message_handler(
        MyProfileMH.context_manager, commands=["profile"], state=None
    )
    dp.register_callback_query_handler(
        MyProfileMH.select_menu, Text(equals="placeholder_callback"), state=ProfileStates.info_about
    )
    dp.register_callback_query_handler(
        MyProfileMH.select_menu, Text(equals="placeholder_callback"), state=ProfileStates.gigs
    )
    dp.register_callback_query_handler(
        MyProfileMH.info_about, Text(equals=MyProfile().info_about_callback), state=ProfileStates.select_menu
    )
    dp.register_callback_query_handler(
        MyProfileMH.my_gigs, Text(equals=MyProfile().gigs_callback), state=ProfileStates.select_menu
    )
    dp.register_callback_query_handler(
        MyProfileMH.edit_menu, Text(equals=MyProfile.update_callback), state=ProfileStates.info_about
    )
    dp.register_callback_query_handler(
        MyProfileMH.edit_username, Text(equals=UpdateProfile().username_callback), state=ProfileStates.info_about
    )
