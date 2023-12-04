import datetime

import aiogram.types
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.types.input_media import InputMediaPhoto, InputFile
from aiogram.types.message import ContentTypes

from aiogram.dispatcher.storage import FSMContext
from man_project_2023.telegram_bot.api.utils_schemas import PayloadStructure
from man_project_2023.telegram_bot.states.states import (
ProfileStates, UpdateDescriptionStates, UpdateUsernameStates, CreateGigStates, CurrentState, State
)
from aiogram.dispatcher.filters import Text
from man_project_2023.telegram_bot.utils.utils import  Utils
from man_project_2023.photos_database.handlers import PhotosDB
from man_project_2023.telegram_bot.keyboards.keyboards import (
    YesOrNo, Controls, MyProfile, Navigation, Filters, DropdownMenu, UpdateProfile,
    InlineKeyboardMarkup, CreateGigMenu, CalendarMenu
)
from man_project_2023.telegram_bot.classes.api_requests import UserAPI, LocationStructure, LocationAPI
from man_project_2023.telegram_bot.config import bot, Dispatcher


utils = Utils()


class Calendar(CalendarMenu):

    def __init__(self):
        self.year: int = 0
        self.month: int = 0
        self.day: int = 0

    def now(self):
        return datetime.datetime.now()

    async def edit(self, callback: CallbackQuery, with_forward: bool = True):
        await callback.message.edit_reply_markup(
            reply_markup=CalendarMenu.keyboard(year=self.year,
                                               month=self.month,
                                               day=self.day,
                                               with_cancel=True,
                                               with_forward=with_forward)
        )

    def reply_markup(self, with_next: bool = False):
        with_forward = False
        now = self.now()
        if self.month < now.month or self.year < now.year:
            with_forward = True
        return CalendarMenu.keyboard(with_cancel=True, with_forward=with_forward, with_next=with_next,
                                     year=self.year, month=self.month, day=1)

    async def move_forward(self, callback: CallbackQuery, state: FSMContext) -> None:
        with_forward = True
        if self.month >= self.now().month and self.year >= self.now().year:
            return
        if self.month + 1 >= self.now().month and self.year >= self.now().year:
            with_forward = False

        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        await self.edit(callback=callback,
                        with_forward=with_forward)

    async def move_bacward(self, callback: CallbackQuery, state: FSMContext) -> None:
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        await self.edit(callback=callback)

    async def update_dates(self) -> None:
        now = datetime.datetime.now()
        self.year = now.year
        self.month = now.month
        self.day = 1


class StateStructure:
    def __init__(self, caption: str, media):
        self.caption = caption
        self.media = media

    def _as_dict(self) -> dict:
        return self.__dict__

class BranchManager:

    def __init__(self):
        self.current_state: CurrentState = None
        self.state: State = None
        self.default_message: dict = {}
        self.message: Message = None
        self.data: dict = {}

    async def state_data(self) -> 'StateStructure':
        state_name = await self.current_state.get_name()
        state_data = self.data[state_name]
        return state_data

    async def set_data(self, state_name: State,
                       caption: str, image_name: str):
        self.data.update({state_name._state: StateStructure(caption=caption,
                                                            media=image_name)})

    async def set(self, message: Message, current_state: CurrentState = None, state = None):
        if current_state is not None:
            self.current_state = current_state

        if message is not None:
            self.default_message = {
                "media": {
                    "media": message.photo[0].file_id,
                    "caption": message.caption,
                    "parse_mode": "Markdown"
                },
                "reply_markup": message.reply_markup
            }
            self.message = message
        if state is not None:
            self.state = state

    async def edit(self):
        data = await self.state_data()
        await self.message.edit_media(media=InputMediaPhoto(
            media=await self.current_state.state_photo(data.media),
            caption=data.caption,
            parse_mode="Markdown"
        ),
        reply_markup=YesOrNo.keyboard(is_inline_keyboard=True))

    async def reset_message(self, *args, **kwargs):
        await self.state.set()
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
                   file_id: str = None,
                   reply_markup: InlineKeyboardMarkup = None,
                   with_placeholder: bool = True):
        if current_state is not None:
            self.current_state = current_state
        edited_message: Message = None
        if self.is_used:

            if not await self.states_equals():
                await self.delete_context_messages()

            try:
                media_id = utils.file_id(self.message)
                media = await self.current_state.state_photo(image=image) if not file_id and image else file_id if file_id else media_id
                edited_message = await self.message.edit_media(media=InputMediaPhoto(
                    media=media,
                    caption=text,
                    parse_mode="Markdown"
                ),
                    reply_markup=DropdownMenu.placeholder_menu(
                        current_menu=await self.current_state.get_placeholder()
                    ) if reply_markup is None and with_placeholder else reply_markup)
                self.message = edited_message
            except Exception as err:
                print(err)
                return None
        self.is_used = True
        return edited_message

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
photos_db = PhotosDB(bot=bot)

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
        await cls.current_state.update_classes(keyboard_class=MyProfile,
                                               state_class=MyProfile)
        await ProfileStates.gigs.set()
        await contextManager.edit(current_state=cls.current_state,
                                  image="dashboard_profile")
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
                                                             [{"text": "Додати оголошення ➕", "callback_data": "add_gig"}]]},
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
    data_for_send = None

    @classmethod
    async def modify_description(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await cls.currentState.set_state(state)
        await UpdateDescriptionStates.description.set()
        cls.data_for_send = PayloadStructure()
        message = await contextManager.edit(text="⌨️ *Уведіть новий опис Вашого профіля:*",
                                            image="dashboard_profile",
                                            reply_markup=UpdateProfile.base_keyboard(with_save=False),
                                            with_placeholder=False)

        await cls.branchManager.set(current_state=cls.currentState,
                                    message=message)

        await cls.branchManager.set_data(state_name=UpdateDescriptionStates.backward_description,
                                         caption="*Ви точно хочете закінчити редагування?*",
                                         image_name="test35459468345687456")

    @classmethod
    async def check_description(cls, message: Message, state: FSMContext) -> None:
        await UpdateDescriptionStates.input_description.set()
        await contextManager.edit(text="👆 Натисніть *\"Зберегти\"* або уведіть *новий опис*:",
                                  image="dashboard_profile",
                                  reply_markup=UpdateProfile.base_keyboard(),
                                  with_placeholder=False)
        if "data" not in message:
            await cls.update_data(message=message,
                                  state=state)

    @classmethod
    async def update_data(cls, message: Message, state: FSMContext) -> None:
        cls.data_for_send.add(description=message.text)
        await message.delete()

    @classmethod
    async def confirm_backward(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await UpdateDescriptionStates.backward_description.set()
        await cls.branchManager.edit()

    @classmethod
    async def save_data(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await UpdateDescriptionStates.confirm_description.set()
        cls.data_for_send.add(telegram_id=state.user)
        await UserAPI.update_description(**cls.data_for_send.as_dict())
        await MyProfileMH.edit_menu(callback=callback,
                                    state=state)

class UpdateUsernameMH:

    @classmethod
    async def modify_username(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer(text="Недоступно",
                              show_alert=True)


class CreateGig:

    current_state: CurrentState = CurrentState(keyboard_class=UpdateProfile,
                                               state_class=CreateGigStates)
    branch_manager: BranchManager = BranchManager()
    data_for_send: PayloadStructure = None
    select_date = Calendar()

    @classmethod
    async def enter_name(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await cls.current_state.set_state(state)
        await CreateGigStates.name.set()
        cls.data_for_send = PayloadStructure()
        edited_message = await contextManager.edit(current_state=cls.current_state,
                                                   text=f"⌨️ *Уведіть назву оголошення:*",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(),
                                                   with_placeholder=False)

        await cls.branch_manager.set(current_state=cls.current_state,
                                     message=edited_message,
                                     state=await cls.current_state.state_attr())
        await cls.branch_manager.set_data(state_name=CreateGigStates.backward,
                                          caption="*Ви точно хочете закінчити редагування?*",
                                          image_name="test35459468345687456")


    @classmethod
    async def check_name(cls, message: Message, state: FSMContext) -> None:

        # TODO: text validation
        cls.data_for_send.add(name=message.text)
        await message.delete()
        edited_message = await contextManager.edit(text=f"Ви увели: *{message.text}*\n\n"
                                                        f""
                                                        f"👆 Натисніть *\"Далі\"* або уведіть *іншу назву*:",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message)

    @classmethod
    async def enter_description(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.description.set()
        edited_message = await contextManager.edit(text=f"⌨️ *Уведіть опис оголошення:*",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message,
                                     state=await cls.current_state.state_attr())

    @classmethod
    async def check_description(cls, message: Message, state: FSMContext) -> None:
        cls.data_for_send.add(description=message.text)
        await message.delete()
        edited_message = await contextManager.edit(text=f"Ви увели: *{message.text}*\n\n"
                                                        f""
                                                        f"👆 Натисніть *\"Далі\"* або уведіть *інший опис*:",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message)

    @classmethod
    async def load_image(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.photo.set()
        edited_message = await contextManager.edit(text=f"⌨️ *Відправте фотографію предмета, який знайшли:*",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(with_faq=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message,
                                     state=await cls.current_state.state_attr())

    @classmethod
    async def check_image(cls, message: Message, state: FSMContext) -> None:

        file_id = utils.file_id(message=message)
        cls.data_for_send.add(photo=file_id)
        await photos_db.save(telegram_id=1125858430,
                             file_id=file_id,
                             gig_id="dfhgbd")
        await message.delete()
        edited_message = await contextManager.edit(text=f"▲ Ви відправили фотографію\n\n"
                                                        f""
                                                        f"👆 Натисніть *\"Далі\"* або відправте *іншу фотографію*:",
                                                   file_id=file_id,
                                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message)

    @classmethod
    async def enter_location(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.location.set()
        edited_message = await contextManager.edit(text=f"⌨️ *Відправте локацію місця, де ви знайшли річ:*",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(with_faq=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message,
                                     state=await cls.current_state.state_attr())

    @classmethod
    async def check_location(cls, message: Message, state: FSMContext) -> None:
        location = utils.location(message=message)
        address = await LocationAPI.get_address(**location)
        city = await LocationStructure(location=address.data).get_city(with_type=True)

        cls.data_for_send.add(location=location,
                              address=address.data)
        await message.delete()
        edited_message = await contextManager.edit(text=f"Ви вказали: *{city}*\n\n"
                                                        f""
                                                        f"👆 Натисніть *\"Далі\"* або відправте локацію *іншого місця*:",
                                                   image="dashboard_profile",
                                                   reply_markup=CreateGigMenu.keyboard(with_next=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message)
        print(f"{city}\n{location}")

    @classmethod
    async def enter_date(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.date.set()
        await cls.select_date.update_dates()
        edited_message = await contextManager.edit(text=f"⌨️ *Оберіть дату, коли була знайдена річ:*",
                                                   image="dashboard_profile",
                                                   reply_markup=cls.select_date.reply_markup(),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message,
                                     state=await cls.current_state.state_attr())

    @classmethod
    async def set_date(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await callback.answer()
        if callback.data.startswith("now"):
            timestamp = utils.now()
        else:
            timestamp = int(callback.data.split("_")[0])
        date = utils.date(timestamp=timestamp)
        edited_message = await contextManager.edit(text=f"Ви обрали *{date}*\n\n"
                                                        f""
                                                        f"👆 Натисніть *\"Далі\"* або оберіть *іншу дату*:",
                                                   reply_markup=cls.select_date.reply_markup(with_next=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message)
        print(timestamp, datetime.datetime.fromtimestamp(timestamp))
        cls.data_for_send.add(date=timestamp)
        print(cls.data_for_send.as_dict())

    @classmethod
    async def confirm_create(cls, callback: CallbackQuery, state: FSMContext) -> None:
        await CreateGigStates.check_data.set()
        address = await LocationStructure(location=cls.data_for_send.address).get_city(with_type=True)
        date = utils.date(timestamp=cls.data_for_send.date)
        edited_message = await contextManager.edit(text=f"🔍 *Перевірте інформацію:*\n\n"
                                                        f""
                                                        f"Назва: *{cls.data_for_send.name}*\n"
                                                        f"Опис: *{cls.data_for_send.description}*\n"
                                                        f"Дата: *{date}*\n"
                                                        f"Місце: *{address}*\n\n"
                                                        f""
                                                        f"*Публікуємо оголошення?*",
                                                   file_id=cls.data_for_send.photo,
                                                   reply_markup=YesOrNo.keyboard(is_inline_keyboard=True),
                                                   with_placeholder=False)
        await cls.branch_manager.set(message=edited_message,
                                     state=await cls.current_state.state_attr())

    @classmethod
    async def confirm_backward(cls, callback: CallbackQuery, state: FSMContext) -> None:
        if not cls.data_for_send.as_dict():
            await MyProfileMH.my_gigs(message=callback.message,
                                      state=state)
            return
        await CreateGigStates.backward.set()
        await cls.branch_manager.edit()


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
        MyProfileMH.edit_menu, Text(equals=UpdateProfile.backward_callback), state=UpdateUsernameStates.username
    )
    dp.register_callback_query_handler(
        MyProfileMH.edit_menu, Text(equals=UpdateProfile.backward_callback), state=UpdateDescriptionStates.description
    )
    dp.register_callback_query_handler(
        MyProfileMH.edit_menu, Text(equals=UpdateProfile.yes_callback), state=UpdateDescriptionStates.backward_description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.modify_description, Text(equals=UpdateProfile().description_callback), state=ProfileStates.edit_menu
    )
    dp.register_callback_query_handler(
        UpdateUsernameMH.modify_username, Text(equals=UpdateProfile().username_callback), state=ProfileStates.edit_menu
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.confirm_backward, Text(equals=Controls.backward_callback), state=UpdateDescriptionStates.input_description
    )
    dp.register_message_handler(
        UpdateDescriptionMH.update_data, state=UpdateDescriptionStates.input_description
    )
    dp.register_message_handler(
        UpdateDescriptionMH.check_description, state=UpdateDescriptionStates.description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.check_description, Text(equals=YesOrNo.no_callback), state=UpdateDescriptionStates.backward_description
    )
    dp.register_callback_query_handler(
        UpdateDescriptionMH.save_data, Text(equals=UpdateProfile.save_callback), state=UpdateDescriptionStates.input_description
    )

    dp.register_callback_query_handler(
        CreateGig.enter_name, Text(equals="add_gig"), state=ProfileStates.gigs
    )
    dp.register_message_handler(
        CreateGig.check_name, state=CreateGigStates.name
    )
    dp.register_callback_query_handler(
        CreateGig.enter_description, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.name
    )
    dp.register_message_handler(
        CreateGig.check_description, state=CreateGigStates.description
    )
    dp.register_callback_query_handler(
        CreateGig.load_image, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.description
    )
    dp.register_message_handler(
        CreateGig.check_image, content_types=ContentTypes.PHOTO, state=CreateGigStates.photo
    )
    dp.register_callback_query_handler(
        CreateGig.enter_location, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.photo
    )
    dp.register_message_handler(
        CreateGig.check_location, content_types=ContentTypes.LOCATION, state=CreateGigStates.location
    )
    dp.register_callback_query_handler(
        CreateGig.enter_date, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.location
    )
    dp.register_callback_query_handler(
        CreateGig.set_date, Text(endswith=CalendarMenu.date_callback), state=CreateGigStates.date
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_create, Text(equals=CreateGigMenu.next_callback), state=CreateGigStates.date
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=CreateGigStates.name
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=CreateGigStates.description
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=CreateGigStates.photo
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=CreateGigStates.location
    )
    dp.register_callback_query_handler(
        CreateGig.confirm_backward, Text(equals=YesOrNo.cancel_callback), state=CreateGigStates.date
    )
    dp.register_callback_query_handler(
        MyProfileMH.my_gigs, Text(equals=YesOrNo.yes_callback), state=CreateGigStates.backward
    )
    dp.register_callback_query_handler(
        CreateGig.branch_manager.reset_message, Text(equals=YesOrNo.no_callback), state=CreateGigStates.backward
    )
    dp.register_callback_query_handler(
        CreateGig.select_date.move_forward, Text(equals=Controls.forward_callback), state=CreateGigStates.date
    )
    dp.register_callback_query_handler(
        CreateGig.select_date.move_bacward, Text(equals=Controls.backward_callback), state=CreateGigStates.date
    )
