import datetime

import aiogram.types
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.types.input_media import InputMediaPhoto, InputFile

from aiogram.dispatcher.storage import FSMContext
from man_project_2023.telegram_bot.states.states import ProfileStates, UpdateDescriptionStates, CurrentState, State
from aiogram.dispatcher.filters import Text
from man_project_2023.telegram_bot.keyboards.keyboards import (
    YesOrNo, Controls, MyProfile, Navigation, Filters, DropdownMenu, UpdateProfile,
    InlineKeyboardMarkup
)
from man_project_2023.telegram_bot.classes.api_requests import UserAPI
from man_project_2023.telegram_bot.config import bot, Dispatcher

class StateStructure:
    def __init__(self, caption: str, media):
        self.caption = caption
        self.media = media

    def _as_dict(self) -> dict:
        return self.__dict__

class BranchManager:

    def __init__(self):
        self.current_state: CurrentState = None
        self.default_message: dict = {}
        self.message: Message = None
        self.data: dict = {}

    # нужно сделать функцию для заполнения функции и чтобы она пейлоадилась в дикт (к примеру текст после нажатия по кнопке с коллбэком и тп)
    # data1: dict = {
    #     "callback1": {
    #
    #     }
    # }

    async def state_data(self) -> 'StateStructure':
        state_name = await self.current_state.get_name()
        state_data = self.data[state_name]
        return state_data

    async def set_data(self, state_name: State,
                       caption: str, photo):
        self.data.update({state_name._state: StateStructure(caption=caption,
                                                            media=photo)})

    async def set(self, current_state: CurrentState, message: Message):
        self.current_state = current_state
        self.default_message = {
            "media": {
                "media": message.photo[0].file_id,
                "caption": message.caption,
                "parse_mode": "Markdown"
            },
            "reply_markup": message.reply_markup
        }
        self.message = message

    async def edit(self):
        data = await self.state_data()
        await self.message.edit_media(media=InputMediaPhoto(
            media=data.media,
            caption=data.caption,
            parse_mode="Markdown"
        ),
        reply_markup=YesOrNo.keyboard(is_inline_keyboard=True))

    async def reset_message(self):
        await self.message.edit_media(media=InputMediaPhoto(
            **self.default_message["media"]
        ),
        reply_markup=self.default_message["reply_markup"])




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


    async def edit(self, current_state: CurrentState = None,
                   text: str = None,
                   image: str = None,
                   reply_markup: InlineKeyboardMarkup = None,
                   with_placeholder: bool = True):
        if current_state is not None:
            self.current_state = current_state
        if self.is_used:

            if not await self.states_equals():
                await self.delete_context_messages()

            try:
                media = await self.current_state.state_photo(image=image)
                edited_message = await self.message.edit_media(media=InputMediaPhoto(
                    media=media,
                    caption=text,
                    parse_mode="Markdown"
                ),
                    reply_markup=DropdownMenu.placeholder_menu(
                        current_menu=await self.current_state.get_placeholder()
                    ) if reply_markup is None else reply_markup)
                return edited_message
            except: return None
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

contextManager = ContextManager()

class MyProfileMH:

    current_state: CurrentState = CurrentState(keyboard_class=MyProfile,
                                               state_class=ProfileStates)
    branchManager: BranchManager = BranchManager()

    @classmethod
    async def select_menu(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await contextManager.select()
        await ProfileStates.select_menu.set()

    @classmethod
    async def context_manager(cls, message: Message, state: FSMContext) -> None:
        await cls.current_state.set_state(state)
        await contextManager.send(current_state=cls.current_state,
                                        required_state=ProfileStates.info_about,
                                        image="dashboard_profile")
        await cls.info_about(message=message,
                             state=state)


    @classmethod
    async def info_about(cls, message: Message, state: FSMContext) -> None:
        await cls.current_state.update_classes(keyboard_class=MyProfile,
                                               state_class=MyProfile)
        await ProfileStates.info_about.set()
        await contextManager.edit(current_state=cls.current_state,
                                        image="dashboard_profile")
        image = open('img/reg_data_board.png', 'rb')

        if not await contextManager.states_equals():
            user_data = await UserAPI.get_user_data(telegram_id=state.user)
            print(user_data)
            await contextManager.appent_delete_list(
                await bot.send_photo(chat_id=state.chat,
                                     caption="📃 *Опис*"
                                             "\n\n"
                                             f"{user_data.data['description']}"
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

        await ProfileStates.gigs.set()
        await contextManager.edit(image="dashboard_profile")
        if not await contextManager.states_equals():
            preview = open('img/423.png', 'rb')
            await contextManager.appent_delete_list(
                await bot.send_photo(chat_id=state.chat,
                                     caption="Я знайшов *чорну куртку*.\n"
                                             "📍 *Кременчук*\n"
                                             "⌚ *Сьогодні, об 16:56*",
                                     photo=preview,
                                     reply_markup={"inline_keyboard": [[{"text": "⚙  Налаштування️", "callback_data": "3754t6"}]]},
                                     parse_mode="Markdown")
            )
            preview = open('img/sh.png', 'rb')
            await contextManager.appent_delete_list(
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
            await contextManager.appent_delete_list(
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

        await cls.current_state.update_classes(keyboard_class=UpdateProfile,
                                               state_class=ProfileStates)
        await ProfileStates.edit_menu.set()
        await contextManager.select(current_state=cls.current_state,
                                          delete_messages=True,
                                          reply_markup=UpdateProfile.keyboard())
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






class UpdateDescriptionMH:

    currentState: CurrentState = CurrentState(keyboard_class=UpdateProfile,
                                              state_class=UpdateDescriptionStates)
    branchManager: BranchManager = BranchManager()

    @classmethod
    async def modify_description(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await cls.currentState.set_state(state)
        await UpdateDescriptionStates.description.set()
        message = await contextManager.edit(text="⌨️ *Уведіть новий опис Вашого профіля:*",
                                            image="dashboard_profile",
                                            reply_markup=UpdateProfile.base_keyboard(with_save=False),
                                            with_placeholder=False)

        await cls.branchManager.set(current_state=cls.currentState,
                                    message=message)
        photo = await cls.currentState.state_photo(image="dashboard_profile")
        await cls.branchManager.set_data(state_name=UpdateDescriptionStates.backward_description,
                                         caption="*Ви точно хочете закінчити редагування?*",
                                         photo=photo)

    @classmethod
    async def check_description(cls, message: Message, state: FSMContext) -> None:
        await UpdateDescriptionStates.input_description.set()
        await contextManager.edit(text="👆 Натисніть *\"Зберегти\"* або уведіть *новий опис*:",
                                  image="dashboard_profile",
                                  reply_markup=UpdateProfile.base_keyboard(),
                                  with_placeholder=False)

        async with state.proxy() as data:
            data["description"] = message.text
        await message.delete()

    @classmethod
    async def confirm_backward(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await UpdateDescriptionStates.backward_description.set()
        await cls.branchManager.edit()

    @classmethod
    async def save_data(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await UpdateDescriptionStates.confirm_description.set()
        async with state.proxy() as data:
            description = data["description"]
        await UserAPI.update_description(telegram_id=state.user,
                                         description=description)
        # await ProfileStates.edit_menu.set()
        # await cls.context_menu_cls.select(current_state=cls.current_state,
        #                                   delete_messages=True,
        #                                   reply_markup=UpdateProfile.keyboard())

    @classmethod
    async def res(cls, callback: CallbackQuery, state: FSMContext) -> None:

        await cls.branchManager.reset_message()



class UpdateUsername:

    @classmethod
    async def modify_username(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await UpdateDescriptionStates.username.set()
        await contextManager.edit(text="⌨️ *Уведіть Ваш новий нікнейм:*",
                                  image="dashboard_profile",
                                  reply_markup=UpdateProfile.base_keyboard(),
                                  with_placeholder=False)




def register_user_handlers(dp: Dispatcher) -> None:
    # dp.register_message_handler(
    #     StartMH.cls_menu, commands=["start"], state=None
    # )
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
        MyProfileMH.info_about, Text(equals=UpdateProfile.backward_callback), state=ProfileStates.edit_menu
    )
    dp.register_callback_query_handler(
        MyProfileMH.my_gigs, Text(equals=MyProfile().gigs_callback), state=ProfileStates.select_menu
    )
    dp.register_callback_query_handler(
        MyProfileMH.edit_menu, Text(equals=MyProfile.update_callback), state=ProfileStates.info_about
    )
    dp.register_callback_query_handler(
        MyProfileMH.edit_menu, Text(equals=UpdateProfile.backward_callback), state=UpdateDescriptionStates.username
    )
    dp.register_callback_query_handler(
        MyProfileMH.edit_menu, Text(equals=UpdateProfile.backward_callback), state=UpdateDescriptionStates.description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.modify_description, Text(equals=UpdateProfile().description_callback), state=ProfileStates.edit_menu
    )
    dp.register_message_handler(
        UpdateDescriptionMH.check_description, state=UpdateDescriptionStates.input_description
    )
    dp.register_message_handler(
        UpdateDescriptionMH.check_description, state=UpdateDescriptionStates.description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.check_description, Text(YesOrNo.no_callback), state=UpdateDescriptionStates.backward_description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.confirm_backward, Text(equals=Controls.backward_callback), state=UpdateDescriptionStates.input_description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.save_data, Text(equals=UpdateProfile.save_callback), state=UpdateDescriptionStates.input_description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.res, Text(equals=UpdateProfile.no_callback), state=UpdateDescriptionStates.confirm_description
    )
