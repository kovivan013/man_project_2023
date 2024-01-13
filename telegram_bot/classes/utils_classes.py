import asyncio
import datetime
from pydantic import BaseModel

from typing import List, ClassVar

from man_project_2023.telegram_bot.config import dp, Dispatcher

from aiogram.types import CallbackQuery, Message
from aiogram.types import InputMediaPhoto, InputFile
from man_project_2023.telegram_bot.config import bot
from man_project_2023.telegram_bot.classes.api_requests import UserAPI, AdminAPI
from man_project_2023.telegram_bot.keyboards.keyboards import (
    YesOrNo, Controls, MyProfile, Navigation, Filters, DropdownMenu, UpdateProfile,
    InlineKeyboardMarkup, CreateGigMenu, CalendarMenu, ListMenu, MainMenu, GigContextMenu
)
from man_project_2023.telegram_bot.utils.utils import Utils
from aiogram.dispatcher.filters.state import State
from man_project_2023.utils.schemas.api_schemas import BaseGig, BaseUser
from man_project_2023.utils.schemas.schemas import GigMessage
from man_project_2023.photos_database.handlers import PhotosDB
from man_project_2023.telegram_bot.api.utils_schemas import StateStructure
from aiogram.dispatcher.storage import FSMContext

utils = Utils()

# class CurrentState:
#
#     def __init__(self, state: FSMContext = None, keyboard_class = None, state_class = None):
#         self.state = state
#         self.keyboard_class = keyboard_class
#         self.state_class = state_class
#
#     async def set_state(self, state: FSMContext):
#         self.state = state
#
#     async def update_classes(self, keyboard_class, state_class):
#         self.keyboard_class = keyboard_class
#         self.state_class = state_class
#
#     async def state_attr(self):
#         return getattr(self.state_class, await self.get_name())
#
#     async def get_state(self) -> dict:
#         state: str = await self.state.get_state()
#         if state is not None:
#             data: list = state.split(":")
#             return {
#                 "name": data[-1],
#                 "group": data[0]
#             }
#         return None
#
#     async def get_name(self):
#         state = await self.get_state()
#         if state is not None:
#             return state["name"]
#         return None
#
#     async def get_group(self):
#         state = await self.get_state()
#         if state is not None:
#             return state["group"]
#         return None
#
#     async def get_state_class(self):
#         return self.state_class()
#
#     async def get_class(self):
#         return self.keyboard_class()
#
#     async def add_reply_markup(self, buttons_list: list,
#                                reply_markup: InlineKeyboardMarkup = None):
#
#         for i in reply_markup.inline_keyboard:
#             row_data: list = []
#             for j in i:
#                 row_data.append(dict(j))
#             buttons_list.append(row_data)
#         return buttons_list
#
#     async def get_buttons(self, mark_current: bool = True,
#                           reply_markup: InlineKeyboardMarkup = None):
#         keyboard = vars(await self.get_class())
#
#         buttons_list: list = []
#         for i, v in keyboard.items():
#             if "callback" not in i:
#                 buttons_list.append([{"text": f"✅ {v}" if mark_current and await self.get_name() == i else v,
#                                       "callback_data": keyboard[i + "_callback"]}])
#
#         return await self.add_reply_markup(buttons_list=buttons_list,
#                                            reply_markup=reply_markup) if reply_markup is not None else buttons_list
#
#     async def get_placeholder(self, required_state: State = None):
#         buttons = vars(await self.get_class())
#         state = await self.get_name()
#         callback: str = "placeholder_callback"
#
#         placeholder: list = {"text": f"✅ {buttons[state] if required_state is None else buttons[required_state._state]} ▼",
#                             "callback_data": callback}
#
#         return placeholder
#
#     async def state_photo(self, image: str):
#         path: str = f"img/states_images/{image}.png"
#         photo = open(path, "rb")
#         return photo
#
# class Calendar(CalendarMenu):
#
#     def __init__(self):
#         self.year: int = 0
#         self.month: int = 0
#         self.day: int = 0
#
#     def now(self):
#         return datetime.datetime.now()
#
#     async def edit(self, callback: CallbackQuery, with_forward: bool = True):
#         await callback.message.edit_reply_markup(
#             reply_markup=CalendarMenu.keyboard(year=self.year,
#                                                month=self.month,
#                                                day=self.day,
#                                                with_cancel=True,
#                                                with_forward=with_forward)
#         )
#
#     def reply_markup(self, with_next: bool = False):
#         with_forward = False
#         now = self.now()
#         if self.month < now.month or self.year < now.year:
#             with_forward = True
#         return CalendarMenu.keyboard(with_cancel=True, with_forward=with_forward, with_next=with_next,
#                                      year=self.year, month=self.month, day=1)
#
#     async def move_forward(self, callback: CallbackQuery, state: FSMContext) -> None:
#         with_forward = True
#         if self.month >= self.now().month and self.year >= self.now().year:
#             return
#         if self.month + 1 >= self.now().month and self.year >= self.now().year:
#             with_forward = False
#
#         if self.month == 12:
#             self.month = 1
#             self.year += 1
#         else:
#             self.month += 1
#         await self.edit(callback=callback,
#                         with_forward=with_forward)
#
#     async def move_bacward(self, callback: CallbackQuery, state: FSMContext) -> None:
#         if self.month == 1:
#             self.month = 12
#             self.year -= 1
#         else:
#             self.month -= 1
#         await self.edit(callback=callback)
#
#     async def update_dates(self) -> None:
#         now = datetime.datetime.now()
#         self.year = now.year
#         self.month = now.month
#         self.day = 1
#
# class ListMenuManager:
#
#     def __init__(self):
#         self.elements_list: list = []
#
#     async def add(self, message: Message) -> None:
#         if element := message.text:
#             await message.delete()
#             if element in self.elements_list:
#                 return ListMenu.keyboard(elements_list=self.elements_list,
#                                          with_next=True)
#             self.elements_list.append(element)
#             return ListMenu.keyboard(elements_list=self.elements_list,
#                                      with_next=True)
#
#     async def remove(self, callback: CallbackQuery, state: FSMContext) -> None:
#         element = callback.data[:callback.data.rindex("_list_menu")]
#         if element in self.elements_list:
#             self.elements_list.remove(element)
#             await callback.message.edit_reply_markup(
#                 reply_markup=ListMenu.keyboard(
#                     elements_list=self.elements_list,
#                     with_skip=True if not self.elements_list else False,
#                     with_next=True if self.elements_list else False
#                 )
#             )
#
#     def reset(self):
#         self.elements_list = []
#
# class BranchManager:
#
#     def __init__(self):
#         self.current_state: CurrentState = None
#         self.state: State = None
#         self.default_message: dict = {}
#         self.message: Message = None
#         self.data: dict = {}
#
#     async def state_data(self) -> 'StateStructure':
#         state_name = await self.current_state.get_name()
#         state_data = self.data[state_name]
#         return state_data
#
#     async def set_data(self, state_name: State,
#                        caption: str, image_name: str):
#         self.data.update({state_name._state: StateStructure(caption=caption,
#                                                             media=image_name)})
#
#     async def set(self, message: Message, current_state: CurrentState = None, state = None):
#         if current_state is not None:
#             self.current_state = current_state
#
#         if message is not None:
#             self.default_message = {
#                 "media": {
#                     "media": message.photo[0].file_id,
#                     "caption": message.caption,
#                     "parse_mode": "Markdown"
#                 },
#                 "reply_markup": message.reply_markup
#             }
#             self.message = message
#         if state is not None:
#             self.state = state
#
#     async def edit(self):
#         data = await self.state_data()
#         await self.message.edit_media(media=InputMediaPhoto(
#             media=await self.current_state.state_photo(data.media),
#             caption=data.caption,
#             parse_mode="Markdown"
#         ),
#         reply_markup=YesOrNo.keyboard(is_inline_keyboard=True))
#
#     async def reset_message(self, *args, **kwargs):
#         await self.state.set()
#         await self.message.edit_media(media=InputMediaPhoto(
#             **self.default_message["media"]
#         ),
#         reply_markup=self.default_message["reply_markup"])
#
# class ContextManager:
#
#     def __init__(self):
#         self.current_state: CurrentState = None
#         self.message: Message = None
#         self.messages_to_delete: list[Message] = []
#         self.previous_state: str = None
#         self.is_used = False
#
#     async def send(self, current_state: CurrentState,
#                    required_state: State, image: str):
#         self.current_state = current_state
#         photo = await self.current_state.state_photo(image=image)
#         self.message = await bot.send_photo(chat_id=self.current_state.state.chat,
#                                             photo=photo,
#                                             reply_markup=DropdownMenu.placeholder_menu(
#                                                current_menu=await self.current_state.get_placeholder(
#                                                    required_state=required_state
#                                                )
#                                            ))
#         return self.message
#
#     async def send_default(self, current_state: CurrentState, text: str,
#                            image: str = "", reply_markup = None):
#
#         self.current_state = current_state
#         chat_id: int = self.current_state.state.chat
#         if image:
#             photo = await self.current_state.state_photo(image=image)
#             self.message = await bot.send_photo(chat_id=chat_id,
#                                                 caption=text,
#                                                 photo=photo,
#                                                 reply_markup=reply_markup,
#                                                 parse_mode="Markdown")
#
#             return self.message
#         await bot.send_message(chat_id=chat_id,
#                                text=text,
#                                reply_markup=reply_markup,
#                                parse_mode="Markdown")
#
#     async def select(self, current_state: CurrentState = None,
#                      delete_messages: bool = False,
#                      reply_markup: InlineKeyboardMarkup = None):
#         if current_state is not None:
#             self.current_state = current_state
#         if delete_messages:
#             await self.delete_context_messages()
#
#         await self.set_previous_state()
#         image = open('img/test35459468345687456.png', 'rb')
#         await self.message.edit_media(media=InputMediaPhoto(
#             media=image,
#             caption=f"💻 *Оберіть необхідне меню:*",
#             parse_mode="Markdown"
#         ),
#             reply_markup=DropdownMenu.menu_keyboard(
#                 buttons=await self.current_state.get_buttons(reply_markup=reply_markup)
#         ))
#
#
#     async def edit(self, current_state: CurrentState = None,
#                    text: str = None,
#                    image: str = None,
#                    file_id: str = None,
#                    reply_markup: InlineKeyboardMarkup = None,
#                    with_placeholder: bool = True):
#         if current_state is not None:
#             self.current_state = current_state
#         edited_message: Message = None
#
#         if not await self.states_equals():
#             await self.delete_context_messages()
#
#         if with_placeholder:
#             keyboard = DropdownMenu.placeholder_menu(
#                     current_menu=await self.current_state.get_placeholder()
#             )
#             if reply_markup is not None:
#                 for i in reply_markup.inline_keyboard:
#                     keyboard.inline_keyboard.append(i)
#         else:
#             keyboard = reply_markup
#
#
#         try:
#             media_id = utils.file_id(self.message)
#             media = await self.current_state.state_photo(image=image) if not file_id and image else file_id if file_id else media_id
#             edited_message = await self.message.edit_media(media=InputMediaPhoto(
#                 media=media,
#                 caption=text,
#                 parse_mode="Markdown"
#             ),
#                 reply_markup=keyboard)
#             self.message = edited_message
#         except Exception as err:
#             print(err)
#             return None
#         return edited_message
#
#     async def appent_delete_list(self, message: Message):
#         self.messages_to_delete.append(message.message_id)
#
#
#     async def delete_context_messages(self):
#         for message_id in self.messages_to_delete:
#             await bot.delete_message(chat_id=self.current_state.state.chat,
#                                      message_id=message_id)
#         self.messages_to_delete.clear()
#
#
#     async def set_previous_state(self):
#         self.previous_state = await self.current_state.get_name()
#
#
#     async def states_equals(self) -> bool:
#         return self.previous_state == await self.current_state.get_name()
#
#
#     async def delete(self):
#         await self.message.delete()
#         await self.delete_context_messages()
#         self.previous_state = None
#         self.reset_data()
#
#
#     def reset_data(self):
#         self.is_used = False

class Storage:

    @property
    def _KEY(self):
        pass

    async def _storage(self, state: FSMContext):
        data = await state.get_data()
        model = type(self)(**data.setdefault(self._KEY, vars(self)))
        return model

    async def _save(self, state: FSMContext, result):
        await state.update_data({self._KEY: vars(result)})

    @staticmethod
    async def _payload(state: FSMContext, dump: bool = False) -> BaseModel:
        storage = await state.get_data()
        data: BaseModel = storage.get("_payload", None)
        return data.model_dump() if dump else data

    @staticmethod
    async def _clear_payload(state: FSMContext):
        data = await state.get_data()
        data.pop("_payload")
        await state.set_data(data)


class CurrentState(Storage):

    _KEY = "current_state"

    def __init__(self, _state = None, keyboard_class = None, state_class = None):
        self._state: State = _state
        self.keyboard_class = keyboard_class
        self.state_class = state_class

    async def set_state(self, state: FSMContext):
        storage: self = await self._storage(state)
        storage._state = state
        await self._save(state, storage)

    async def update_classes(self, state: FSMContext, keyboard_class, state_class):
        storage: self = await self._storage(state)
        storage.keyboard_class = keyboard_class
        storage.state_class = state_class
        await self._save(state, storage)


    async def state_attr(self, state: FSMContext):
        storage: self = await self._storage(state)
        return getattr(storage.state_class, await self.get_name(state))

    async def get_state(self, state: FSMContext) -> dict:
        instance = await state.get_state()
        if instance is not None:
            data: list = instance.split(":")
            return {
                "name": data[-1],
                "group": data[0]
            }
        return None

    async def get_name(self, state: FSMContext):
        data: dict = await self.get_state(state)
        if data is not None:
            return data["name"]
        return None

    async def get_group(self, state: FSMContext):
        data: dict = await self.get_state(state)
        if data is not None:
            return data["group"]
        return None

    async def get_state_class(self, state: FSMContext):
        storage: self = await self._storage(state)
        return storage.state_class()

    async def get_class(self, state: FSMContext):
        storage: self = await self._storage(state)
        return storage.keyboard_class()

    async def add_reply_markup(self, buttons_list: list,
                               reply_markup: InlineKeyboardMarkup = None):

        for i in reply_markup.inline_keyboard:
            row_data: list = []
            for j in i:
                row_data.append(dict(j))
            buttons_list.append(row_data)
        return buttons_list

    async def get_buttons(self, state: FSMContext, mark_current: bool = True,
                          reply_markup: InlineKeyboardMarkup = None):
        storage: self = await self._storage(state)
        keyboard = vars(await self.get_class(state))
        buttons_list: list = []

        for i, v in keyboard.items():
            if "callback" not in i:
                buttons_list.append([{"text": f"✅ {v}" if mark_current and await self.get_name(state) == i else v,
                                      "callback_data": keyboard[i + "_callback"]}])

        return await self.add_reply_markup(buttons_list=buttons_list,
                                          reply_markup=reply_markup) if reply_markup is not None else buttons_list

    async def get_placeholder(self, state: FSMContext, required_state: State = None):
        storage: self = await self._storage(state)
        buttons = vars(await self.get_class(state))
        name = await self.get_name(state)
        callback: str = "placeholder_callback"

        placeholder: list = {"text": f"✅ {buttons[name] if required_state is None else buttons[required_state._state]} ▼",
                            "callback_data": callback}

        return placeholder

    async def state_photo(self, image: str):
        path: str = f"img/states_images/{image}.png"
        photo = open(path, "rb")
        return photo


class Calendar(CalendarMenu, Storage):

    _KEY = "calendar"

    def __init__(self, year: int = 0, month: int = 0, day: int = 0):
        self.year = year
        self.month = month
        self.day = day

    def now(self):
        return datetime.datetime.now()

    async def edit(self, state: FSMContext, callback: CallbackQuery, with_forward: bool = True):
        storage: self = await self._storage(state)
        await callback.message.edit_reply_markup(
            reply_markup=CalendarMenu.keyboard(year=storage.year,
                                               month=storage.month,
                                               day=storage.day,
                                               with_cancel=True,
                                               with_forward=with_forward)
        )

    async def reply_markup(self, state: FSMContext, with_next: bool = False):
        storage: self = await self._storage(state)
        with_forward = False
        now = self.now()
        if storage.month < now.month or storage.year < now.year:
            with_forward = True
        await self._save(state, storage)
        return CalendarMenu.keyboard(with_cancel=True, with_forward=with_forward, with_next=with_next,
                                     year=storage.year, month=storage.month, day=1)


    async def move_forward(self, callback: CallbackQuery, state: FSMContext) -> None:
        storage: self = await self._storage(state)
        with_forward = True
        now = self.now()
        if storage.month >= now.month and storage.year >= now.year:
            return
        if storage.month + 1 >= now.month and storage.year >= now.year:
            with_forward = False

        if storage.month == 12:
            storage.month = 1
            storage.year += 1
        else:
            storage.month += 1
        await self._save(state, storage)
        await self.edit(state=state,
                        callback=callback,
                        with_forward=with_forward)

    async def move_bacward(self, callback: CallbackQuery, state: FSMContext) -> None:
        storage: self = await self._storage(state)
        if storage.month == 1:
            storage.month = 12
            storage.year -= 1
        else:
            storage.month -= 1
        await self._save(state, storage)
        await self.edit(state=state,
                        callback=callback)

    async def update_dates(self, state: FSMContext) -> None:
        storage: self = await self._storage(state)
        now = self.now()
        storage.year = now.year
        storage.month = now.month
        storage.day = 1
        await self._save(state, storage)


class ListMenuManager(Storage):

    _KEY = "list_menu_manager"

    def __init__(self, elements_list: list = []):
        self.elements_list = elements_list

    async def _elements_list(self, state: FSMContext):
        storage: self = await self._storage(state)
        return storage.elements_list

    async def add(self, state: FSMContext, message: Message) -> None:
        storage: self = await self._storage(state)
        if element := message.text:
            await message.delete()
            if element in storage.elements_list:
                return ListMenu.keyboard(elements_list=storage.elements_list,
                                         with_next=True)
            storage.elements_list.append(element)
            await self._save(state, storage)
            return ListMenu.keyboard(elements_list=storage.elements_list,
                                     with_next=True)

    async def remove(self, callback: CallbackQuery, state: FSMContext) -> None:
        storage: self = await self._storage(state)
        element = callback.data[:callback.data.rindex("_list_menu")]
        if element in storage.elements_list:
            storage.elements_list.remove(element)
            await self._save(state, storage)
            await callback.message.edit_reply_markup(
                reply_markup=ListMenu.keyboard(
                    elements_list=storage.elements_list,
                    with_skip=True if not storage.elements_list else False,
                    with_next=True if storage.elements_list else False
                )
            )

    async def reset(self, state: FSMContext):
        storage: self = await self._storage(state)
        self.elements_list = []
        await self._save(state, storage)


class BranchManager(Storage):

    _KEY = "branch_manager"

    def __init__(self, _state: State = None, current_state: CurrentState = None,
                 default_message: dict = {}, message: Message = None, data: dict = {}):
        self._state = _state
        self.current_state = current_state
        self.default_message = default_message
        self.message = message
        self.data = data

    async def state_data(self, state: FSMContext) -> 'StateStructure':
        storage: self = await self._storage(state)
        state_name = await storage.current_state.get_name(state)
        state_data = storage.data[state_name]
        return state_data

    async def set_data(self, state: FSMContext, state_name: State,
                       caption: str, image_name: str):
        storage: self = await self._storage(state)
        storage.data.update({state_name._state: StateStructure(caption=caption,
                                                               media=image_name)})
        await self._save(state, storage)

    async def set(self, state: FSMContext, message: Message, current_state: CurrentState = None, _state = None):
        storage: self = await self._storage(state)
        if current_state is not None:
            storage.current_state = current_state

        if message is not None:
            storage.default_message = {
                "media": {
                    "media": message.photo[0].file_id,
                    "caption": message.caption,
                    "parse_mode": "Markdown"
                },
                "reply_markup": message.reply_markup
            }
            storage.message = message
        if _state is not None:
            storage._state = _state
        await self._save(state, storage)

    async def edit(self, state: FSMContext):
        storage: self = await self._storage(state)
        data = await self.state_data(state)
        await storage.message.edit_media(media=InputMediaPhoto(
            media=await storage.current_state.state_photo(data.media),
            caption=data.caption,
            parse_mode="Markdown"
        ),
        reply_markup=YesOrNo.keyboard(is_inline_keyboard=True))

    async def reset_message(self, message: Message, state: FSMContext):
        storage: self = await self._storage(state)
        await storage._state.set()
        await storage.message.edit_media(media=InputMediaPhoto(
            **storage.default_message["media"]
        ),
        reply_markup=storage.default_message["reply_markup"])


class ContextManager(Storage):

    _KEY = "context_manager"

    def __init__(self, current_state: CurrentState = None, message: Message = None,
                 messages_to_delete: List[Message] = [], previous_state: str = None):
        self.current_state = current_state
        self.message = message
        self.messages_to_delete = messages_to_delete
        self.previous_state = previous_state

    async def send(self, state: FSMContext, current_state: CurrentState,
                   required_state: State, image: str):
        """
        Отправляет сообщение сразу с плэйсхолдером (подменю в котором находится пользователь)
        :param current_state:
        :param required_state:
        :param image:
        :return:
        """
        storage: self = await self._storage(state)
        storage.current_state = current_state
        photo = await storage.current_state.state_photo(image=image)
        storage.message = await bot.send_photo(chat_id=state.chat,
                                               photo=photo,
                                               reply_markup=DropdownMenu.placeholder_menu(
                                                   current_menu=await storage.current_state.get_placeholder(
                                                       state=state,
                                                       required_state=required_state
                                                   )
                                               ))
        await self._save(state, storage)
        return storage.message

    async def send_default(self, state: FSMContext, current_state: CurrentState, text: str,
                           image: str = "", reply_markup = None):
        """
        Отравляет сообщение без клавиатуры с плейсхолдером (подменю в котором сейчас находится пользователь)
        :param current_state:
        :param text:
        :param image:
        :param reply_markup:
        :return:
        """
        storage: self = await self._storage(state)
        storage.current_state = current_state
        chat_id: int = state.chat
        if image:
            photo = await storage.current_state.state_photo(image=image)
            storage.message = await bot.send_photo(chat_id=chat_id,
                                                   caption=text,
                                                   photo=photo,
                                                   reply_markup=reply_markup,
                                                   parse_mode="Markdown")
            await self._save(state, storage)
            return storage.message
        await bot.send_message(chat_id=chat_id,
                               text=text,
                               reply_markup=reply_markup,
                               parse_mode="Markdown")
        await self._save(state, storage)

    async def select(self, state: FSMContext, current_state: CurrentState = None,
                     delete_messages: bool = False,
                     reply_markup: InlineKeyboardMarkup = None):

        if delete_messages:
            await self.delete_context_messages(state)
        await self.set_previous_state(state)

        storage: self = await self._storage(state)
        if current_state is not None:
            storage.current_state = current_state

        image = open('img/test35459468345687456.png', 'rb')
        await storage.message.edit_media(media=InputMediaPhoto(
            media=image,
            caption=f"💻 *Оберіть необхідне меню:*",
            parse_mode="Markdown"
        ),
            reply_markup=DropdownMenu.menu_keyboard(
                buttons=await storage.current_state.get_buttons(
                    state=state,
                    reply_markup=reply_markup
                )
        ))
        await self._save(state, storage)

    async def edit(self, state: FSMContext, current_state: CurrentState = None,
                   text: str = None, image: str = None, file_id: str = None,
                   reply_markup: InlineKeyboardMarkup = None, with_placeholder: bool = True):

        if not await self.states_equals(state):
            await self.delete_context_messages(state)

        storage: self = await self._storage(state)
        if current_state is not None:
            storage.current_state = current_state
        edited_message: Message = None

        if with_placeholder:
            keyboard = DropdownMenu.placeholder_menu(
                    current_menu=await storage.current_state.get_placeholder(
                        state=state
                    )
            )
            if reply_markup is not None:
                for i in reply_markup.inline_keyboard:
                    keyboard.inline_keyboard.append(i)
        else:
            keyboard = reply_markup


        try:
            media_id = utils.file_id(storage.message)
            media = await storage.current_state.state_photo(image=image) if not file_id and image \
                else file_id if file_id \
                else media_id
            edited_message = await storage.message.edit_media(media=InputMediaPhoto(
                media=media,
                caption=text,
                parse_mode="Markdown"
            ),
                reply_markup=keyboard)
            storage.message = edited_message
        except Exception as err:
            print(err)
            return None
        await self._save(state, storage)
        return edited_message

    async def appent_delete_list(self, state: FSMContext, message: Message):
        storage: self = await self._storage(state)
        storage.messages_to_delete.append(message.message_id)
        await self._save(state, storage)

    async def delete_context_messages(self, state: FSMContext):
        storage: self = await self._storage(state)
        for message_id in storage.messages_to_delete:
            await bot.delete_message(chat_id=state.chat,
                                     message_id=message_id)
        storage.messages_to_delete = []
        await self._save(state, storage)

    async def set_previous_state(self, state: FSMContext):
        storage: self = await self._storage(state)
        storage.previous_state = await current_state.get_name(state)
        await self._save(state, storage)

    async def states_equals(self, state: FSMContext) -> bool:
        storage: self = await self._storage(state)
        return storage.previous_state == await storage.current_state.get_name(state)


    async def delete(self, state: FSMContext):
        await self.delete_context_messages(state)
        storage: self = await self._storage(state)
        await storage.message.delete()
        storage.previous_state = None
        await self._save(state, storage)

current_state = CurrentState()
calendar_menu = Calendar()
list_manager = ListMenuManager()
branch_manager = BranchManager()
context_manager = ContextManager()

class DropdownManager:
    pass



class Marketplace:
    """
    Класс который обеспечивает работу системы поиска проекта, также все функции связанные с собственными объявлениями пользователя
    Функции фильтров и прочего
    """
    on_page_gigs: list = []
    open_id: int = 0

    @staticmethod
    def date(timestamp: int):
        now = utils.now(timestamp=False)
        date = datetime.datetime.fromtimestamp(timestamp)
        today = all([date.year == now.year,
                    date.month == now.month,
                    date.day == now.day])
        yesterday = all([date.year == now.year,
                        date.month == now.month,
                        date.day == (now - datetime.timedelta(days=1)).day])
        timing = f"{date.hour}:{date.minute if date.minute > 9 else f'0{date.minute}'}"
        if today:
            time = f"Сьогодні, о {timing}"
        elif yesterday:
            time = f"Учора, о {timing}"
        else:
            time = f"{date.day if date.day > 9 else f'0{date.day}'}.{date.month if date.month > 9 else f'0{date.month}'}.{date.year}"

        return time

    @classmethod
    async def get_user_gigs(cls, telegram_id: int = 0,
                            city: str = "",
                            limit: int = 5,
                            page: int = 1,
                            from_date: str = "latest",
                            type: str = "active") -> List[GigMessage]:
        # if telegram_id:
        response = await UserAPI.get_user_gigs(telegram_id=telegram_id,
                                               city=city,
                                               limit=limit,
                                               page=page,
                                               from_date=from_date,
                                               type=type)
        # elif not telegram_id:
        #     response = await UserAPI.get_gigs(limit=limit,
        #                                       page=page,
        #                                       type=type)
        if response._success:
            response_messages: list = []

            gigs = response.data

            for i, v in gigs.items():
                message_data: GigMessage = GigMessage()
                gig = BaseGig().model_validate(v)
                time = cls.date(timestamp=gig.data.date)
                message_data.telegram_id = gig.telegram_id
                message_data.id = gig.id
                message_data.text: str = f"{gig.data.name}\n\n" \
                                         f"" \
                                         f"📍 *{gig.data.location.data.name}*\n" \
                                         f"⌚ *{time}*"
                response_messages.append(message_data)
            return response_messages
        return None

    @classmethod
    async def get_gigs(cls, request: str,
                       city: str = "",
                       limit: int = 5,
                       page: int = 1,
                       from_date: str = "latest",
                       type: str = "active") -> List[GigMessage]:
        response = await UserAPI.get_gigs(request=request,
                                          city=city,
                                          limit=limit,
                                          page=page,
                                          from_date=from_date,
                                          type=type)
        # if telegram_id:
        #     response = await UserAPI.get_user_gigs(telegram_id=telegram_id,
        #                                            limit=limit,
        #                                            page=page,
        #                                            type=type)
        # elif not telegram_id:
        #     response = await UserAPI.get_gigs(limit=limit,
        #                                       page=page,
        #                                       type=type)
        if response._success:
            response_messages: list = []

            gigs = response.data

            for i, v in gigs.items():
                message_data: GigMessage = GigMessage()
                gig = BaseGig().model_validate(v)
                time = cls.date(timestamp=gig.data.date)
                message_data.telegram_id = gig.telegram_id
                message_data.id = gig.id
                message_data.text: str = f"{gig.data.name}\n\n" \
                                         f"" \
                                         f"📍 *{gig.data.location.data.name}*\n" \
                                         f"⌚ *{time}*"
                response_messages.append(message_data)
            return response_messages
        return None

    @classmethod
    async def send_gigs(cls, state: FSMContext, request: str = "",
                        telegram_id: int = 0, city: str = "", limit: int = 5, page: int = 1,
                        from_date: str = "latest", type: str = "active", from_saved: bool = False):
        if request:
            gigs = await cls.get_gigs(request=request,
                                      city=city,
                                      limit=limit,
                                      page=page,
                                      from_date=from_date,
                                      type=type)
        elif telegram_id:
            gigs = await cls.get_user_gigs(telegram_id=telegram_id,
                                           city=city,
                                           limit=limit,
                                           page=page,
                                           from_date=from_date,
                                           type=type)
        else:
            if from_saved:
                gigs = cls.on_page_gigs
            else:
                cls.on_page_gigs = gigs

        for gig in gigs:
            await context_manager.appent_delete_list(
                state=state,
                message=await bot.send_photo(chat_id=gig.telegram_id,
                                             photo=InputFile(PhotosDB.get(telegram_id=gig.telegram_id,
                                                                          gig_id=gig.id)),
                                             caption=gig.text,
                                             reply_markup=GigContextMenu.keyboard(telegram_id=gig.telegram_id,
                                                                                  gig_id=gig.id),
                                             parse_mode="Markdown",
                                             disable_notification=True)
            )

    @classmethod
    async def keyboard_control(cls, callback: CallbackQuery, state: FSMContext):
        if callback.data == GigContextMenu.back_callback:
            await callback.message.edit_reply_markup(
                reply_markup=GigContextMenu.keyboard()
            )
            cls.open_id = 0

        if callback.data.endswith(GigContextMenu.placeholder_callback):
            value: str = callback.data[:callback.data.rindex(GigContextMenu.placeholder_callback)]
            if cls.open_id:
                try:
                    await bot.edit_message_reply_markup(
                        chat_id=state.chat,
                        message_id=cls.open_id,
                        reply_markup=GigContextMenu.keyboard()
                    )
                except:
                    cls.open_id = 0

            telegram_id, gig_id = tuple(value.split("_"))
            await callback.message.edit_reply_markup(
                reply_markup=GigContextMenu.keyboard(open=True,
                                                     telegram_id=telegram_id,
                                                     gig_id=gig_id)
            )
            cls.open_id = callback.message.message_id


# import asyncio
# m = Marketplace()
# r = asyncio.run(m.get_user_gigs(telegram_id=1125858430, limit=2, page=1))
# print(r)





