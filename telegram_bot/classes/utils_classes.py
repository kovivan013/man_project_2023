import asyncio
import datetime
from pydantic import BaseModel

from typing import List, Union, Callable

from man_project_2023.telegram_bot.config import dp, Dispatcher

from aiogram.types import CallbackQuery, Message
from aiogram.types import InputMediaPhoto, InputFile
from man_project_2023.telegram_bot.config import bot
from man_project_2023.telegram_bot.classes.api_requests import UserAPI, AdminAPI, LocationAPI
from man_project_2023.telegram_bot.keyboards.keyboards import (
    YesOrNo, Controls, MyProfile, Filters, DropdownMenu, UpdateProfile, InlineKeyboardMarkup,
    CreateGigMenu, CalendarMenu, ListMenu, MainMenu, GigContextMenu, default_inline_keyboard
)
from man_project_2023.telegram_bot.states.states import FiltersStates
from man_project_2023.telegram_bot.utils.utils import Utils
from aiogram.dispatcher.filters.state import State
from man_project_2023.utils.schemas.api_schemas import BaseGig, BaseUser, GigsResponse
from man_project_2023.utils.schemas.schemas import GigMessage
from man_project_2023.photos_database.handlers import PhotosDB
from man_project_2023.telegram_bot.api.utils_schemas import StateStructure, LocationStructure
from aiogram.dispatcher.storage import FSMContext

utils = Utils()

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


current_state = CurrentState()


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


calendar_menu = Calendar()


class ListMenuManager(Storage):

    _KEY = "list_menu_manager"

    def __init__(self, elements_list: list = []):
        self.elements_list = elements_list

    async def _elements_list(self, state: FSMContext, clear: bool = False):
        storage: self = await self._storage(state)
        elements = storage.elements_list
        if clear:
            storage.elements_list = []
            await self._save(state, storage)
        return elements

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

        # with_ready = False
        # for i in callback.message.reply_markup.inline_keyboard:
        #     for v in i:
        #         if "with_ready" in v.callback_data:
        #             with_ready = True

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


list_manager = ListMenuManager()


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
            storage: self = await self._storage(state)
            if storage.message: print(storage.message.message_id, "send_default")
            return storage.message
        storage.message = await bot.send_message(chat_id=chat_id,
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

        keyboard = reply_markup

        if with_placeholder:
            keyboard = DropdownMenu.placeholder_menu(
                current_menu=await storage.current_state.get_placeholder(
                    state=state
                )
            )
        if reply_markup is not None:
            keyboard = InlineKeyboardMarkup()
            if not isinstance(instance := reply_markup, list):
                instance = [reply_markup]
            for i in instance:
                for v in i.inline_keyboard:
                    keyboard.inline_keyboard.append(v)




        try:
            media_id = utils.file_id(storage.message)
            media = await storage.current_state.state_photo(image=image) if not file_id and image \
                else file_id if file_id \
                else media_id

            if storage.message: print(storage.message.message_id, "edit")
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
        for i, message_id in enumerate(storage.messages_to_delete.copy()):
            try:
                if await bot.delete_message(chat_id=state.chat,
                                            message_id=message_id):
                    storage.messages_to_delete.pop(i)
            except:
                pass
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
        try:
            await storage.message.delete()
            storage.message = None
        except: pass
        storage.previous_state = None
        await self._save(state, storage)

    async def reset(self, state: FSMContext):
        storage: self = await self._storage(state)
        await self.delete(state)
        storage.current_state = None
        await self._save(state, storage)


context_manager = ContextManager()


class FiltersManager(Storage):

    _KEY = "filters_manager"

    time_signs: dict = {
        "latest": "нових",
        "oldest": "старих",
    }

    def __init__(self, time: str = "latest", city: str = "all", tags: list = []):
        self.time = time
        self.city = city
        self.tags = tags

    async def get_filters(self, state: FSMContext):
        storage: self = await self._storage(state)
        return storage

    async def reset_filters(self, state: FSMContext):
        storage: self = await self._storage(state)
        storage.time = "latest"
        storage.city = "all"
        storage.tags = []
        await self._save(state, storage)

    async def filters_menu(self, callback: CallbackQuery, state: FSMContext):
        await FiltersStates.filters.set()
        storage: self = await self._storage(state)
        await context_manager.edit(state=state,
                                   image="filters",
                                   reply_markup=Filters.keyboard(time=storage.time,
                                                                 city=storage.city,
                                                                 tags=len(storage.tags)),
                                   with_placeholder=False)
        await context_manager.delete_context_messages(state)

    async def time_filter(self, callback: CallbackQuery, state: FSMContext):
        await FiltersStates.time_filter.set()
        storage: self = await self._storage(state)
        image = await current_state.state_photo(image="time")
        await callback.message.edit_media(media=InputMediaPhoto(
            media=image,
            caption=f"⌚ Починати з *{self.time_signs[storage.time]}* оголошень:",
            parse_mode="Markdown"
        ),
        reply_markup=Filters.time_keyboard(time=storage.time)
        )

    async def set_time(self, callback: CallbackQuery, state: FSMContext):
        storage: self = await self._storage(state)
        storage.time = callback.data
        image = await current_state.state_photo(image="time")
        await callback.message.edit_media(media=InputMediaPhoto(
            media=image,
            caption=f"⌚ Починати з *{self.time_signs[storage.time]}* оголошень:",
            parse_mode="Markdown"
        ),
        reply_markup=Filters.time_keyboard(time=callback.data)
        )
        await storage._save(state, storage)


    async def location_filter(self, callback: CallbackQuery, state: FSMContext):
        await FiltersStates.location_filter.set()
        storage: self = await self._storage(state)
        image = await current_state.state_photo(image="location")
        await callback.message.edit_media(media=InputMediaPhoto(
            media=image,
            caption=f"📍 Відправте назву локації, у межах якої хочете фільтрувати оголошення:",
            parse_mode="Markdown"
        ),
            reply_markup=Filters.location_keyboard()
        )

    async def set_location(self, message: Message, state: FSMContext):
        # TODO: location reset to default value
        storage: self = await self._storage(state)
        storage.city = message.text
        await message.delete()
        location = await LocationAPI.get_location(name=storage.city)
        address = await LocationAPI.get_address(**location)
        city = await LocationStructure(location=address.data).get_city(with_type=True,
                                                                       case=1)
        await context_manager.edit(
            state=state,
            image="location",
            text=f"📍 Фільтрувати в межах *{' '.join(city.values())}*",
            reply_markup=Filters.location_keyboard(),
            with_placeholder=False
        )
        await storage._save(state, storage)

    async def reset_location(self, callback: CallbackQuery, state: FSMContext):
        storage: self = await self._storage(state)
        storage.city = "all"
        await self._save(state, storage)
        await self.filters_menu(callback=callback,
                                state=state)

    async def tags_filter(self, callback: CallbackQuery, state: FSMContext):
        await FiltersStates.tags_filter.set()
        storage: self = await self._storage(state)
        image = await current_state.state_photo(image="tags")
        await callback.message.edit_media(media=InputMediaPhoto(
            media=image,
            caption=f"❌ *Натисніть на тег, щоб видалити його.*",
            parse_mode="Markdown"
        ),
        reply_markup=ListMenu.keyboard(elements_list=storage.tags,
                                       with_ready=True)
        )

    async def add_tag(self, message: Message, state: FSMContext):
        storage: self = await self._storage(state)
        if message.text not in storage.tags:
            storage.tags.append(message.text)
        await message.delete()
        await context_manager.edit(state=state,
                                   image="tags",
                                   text=f"❌ *Натисніть на тег, щоб видалити його.*",
                                   reply_markup=ListMenu.keyboard(elements_list=storage.tags,
                                                                  with_ready=True),
                                   with_placeholder=False)
        await self._save(state, storage)

    async def remove_tag(self, callback: CallbackQuery, state: FSMContext):
        storage: self = await self._storage(state)
        element = callback.data[:callback.data.rindex("_list_menu")]

        if element in storage.tags:
            storage.tags.remove(element)
            await self._save(state, storage)
            await callback.message.edit_reply_markup(
                reply_markup=ListMenu.keyboard(
                    elements_list=storage.tags,
                    with_ready=True
                )
            )

filters_manager = FiltersManager()

class DropdownManager:
    pass



class Marketplace(Storage):
    """
    Класс который обеспечивает работу системы поиска проекта, также все функции связанные с собственными объявлениями пользователя
    Функции фильтров и прочего
    """

    _KEY = "marketplace"

    def __init__(self, document: GigsResponse = GigsResponse(), gigs: list = [], open_id: int = 0):
        self.document = document
        self.gigs = gigs
        self.open_id = open_id

    async def _document(self, state: FSMContext):
        storage: self = await self._storage(state)
        return storage.document

    async def set_request(self, state: FSMContext, key: str):
        storage: self = await self._storage(state)
        storage.document.key = key
        await self._save(state, storage)

    async def next_page(self, state: FSMContext) -> 'GigsResponse':
        storage: self = await self._storage(state)
        if storage.document.page < storage.document.pages:
            storage.document.page += 1
        await self._save(state, storage)
        return storage.document

    async def previous_page(self, state: FSMContext) -> 'GigsResponse':
        storage: self = await self._storage(state)
        if storage.document.page > 1:
            storage.document.page -= 1
        await self._save(state, storage)
        return storage.document

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

    async def get_user_gigs(self, state: FSMContext, telegram_id: int,
                            city: str = "",
                            limit: int = 3,
                            page: int = 1,
                            from_date: str = "latest",
                            type: str = "active") -> 'GigsResponse':
        storage: self = await self._storage(state)
        response = await UserAPI.get_user_gigs(telegram_id=telegram_id,
                                               city=city,
                                               limit=limit,
                                               page=page,
                                               from_date=from_date,
                                               type=type)
        if response._success:
            response_messages: list = []

            gigs = response.data["gigs"]
            document = GigsResponse().model_validate(response.data["response"])
            storage.document = document

            for i, v in gigs.items():
                message_data: GigMessage = GigMessage()
                gig = BaseGig().model_validate(v)
                time = self.date(timestamp=gig.data.date)
                message_data.telegram_id = gig.telegram_id
                message_data.id = gig.id
                message_data.text: str = f"{gig.data.name}\n\n" \
                                         f"" \
                                         f"📍 *{gig.data.location.data.name}*\n" \
                                         f"⌚ *{time}*"
                response_messages.append(message_data)
            storage.gigs = response_messages
            await self._save(state, storage)
            return document
        return None

    async def get_gigs(self, state: FSMContext,
                       request: str,
                       city: str = "",
                       limit: int = 2,
                       page: int = 1,
                       from_date: str = "latest",
                       type: str = "active") -> 'GigsResponse':
        storage: self = await self._storage(state)
        filters = await filters_manager.get_filters(state)
        # TODO: add tag filter to backend search function
        response = await UserAPI.get_gigs(request=request,
                                          city=filters.city,
                                          limit=limit,
                                          page=page,
                                          from_date=filters.time,
                                          type=type)
        if response._success:
            response_messages: list = []
            gigs = response.data["gigs"]
            document = GigsResponse().model_validate(response.data["response"])
            storage.document = document

            for i, v in gigs.items():
                message_data: GigMessage = GigMessage()
                gig = BaseGig().model_validate(v)
                time = self.date(timestamp=gig.data.date)
                message_data.telegram_id = gig.telegram_id
                message_data.id = gig.id
                message_data.text: str = f"{gig.data.name}\n\n" \
                                         f"" \
                                         f"📍 *{gig.data.location.data.name}*\n" \
                                         f"⌚ *{time}*"
                response_messages.append(message_data)
            storage.gigs = response_messages
            await self._save(state, storage)
            return document
        return None

    async def send_gigs(self, state: FSMContext, reply_markup: Callable):
        # cls, state: FSMContext, request: str = "",
        # telegram_id: int = 0, city: str = "", limit: int = 5, page: int = 1,
        # from_date: str = "latest", type: str = "active", from_saved: bool = False
        # if request:
        #     gigs = await cls.get_gigs(request=request,
        #                               city=city,
        #                               limit=limit,
        #                               page=page,
        #                               from_date=from_date,
        #                               type=type)
        # elif telegram_id:
        #     gigs = await cls.get_user_gigs(telegram_id=telegram_id,
        #                                    city=city,
        #                                    limit=limit,
        #                                    page=page,
        #                                    from_date=from_date,
        #                                    type=type)
        # else:
        #     if from_saved:
        #         gigs = cls.on_page_gigs
        #     else:
        #         cls.on_page_gigs = gigs
        storage: self = await self._storage(state)
        for gig in storage.gigs:
            print(gig.telegram_id)
            await context_manager.appent_delete_list(
                state=state,
                message=await bot.send_photo(chat_id=state.user,
                                             photo=InputFile(PhotosDB.get(telegram_id=gig.telegram_id,
                                                                          gig_id=gig.id)),
                                             caption=gig.text,
                                             reply_markup=reply_markup(telegram_id=gig.telegram_id,
                                                                       gig_id=gig.id),
                                             parse_mode="Markdown",
                                             disable_notification=True)
            )

    async def keyboard_control(self, callback: CallbackQuery, state: FSMContext):
        storage: self = await self._storage(state)
        if callback.data == GigContextMenu.back_callback:
            await callback.message.edit_reply_markup(
                reply_markup=GigContextMenu.keyboard()
            )
            storage.open_id = 0

        if callback.data.endswith(GigContextMenu.placeholder_callback):
            value: str = callback.data[:callback.data.rindex(GigContextMenu.placeholder_callback)]
            if storage.open_id:
                try:
                    await bot.edit_message_reply_markup(
                        chat_id=state.chat,
                        message_id=storage.open_id,
                        reply_markup=GigContextMenu.keyboard()
                    )
                except:
                    storage.open_id = 0

            telegram_id, gig_id = tuple(value.split("_"))
            await callback.message.edit_reply_markup(
                reply_markup=GigContextMenu.keyboard(open=True,
                                                     telegram_id=telegram_id,
                                                     gig_id=gig_id)
            )
            storage.open_id = callback.message.message_id

        await self._save(state, storage)



marketplace = Marketplace()


# import asyncio
# m = Marketplace()
# r = asyncio.run(m.get_user_gigs(telegram_id=1125858430, limit=2, page=1))
# print(r)





