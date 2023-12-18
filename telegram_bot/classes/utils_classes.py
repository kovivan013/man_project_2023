import datetime

from aiogram.types import CallbackQuery, Message
from man_project_2023.telegram_bot.config import bot
from man_project_2023.telegram_bot.classes.api_requests import UserAPI, AdminAPI
from man_project_2023.telegram_bot.keyboards.keyboards import CalendarMenu, InlineKeyboardMarkup, DropdownMenu
from aiogram.types import InputMediaPhoto, InputFile
from man_project_2023.telegram_bot.utils.utils import Utils
from aiogram.dispatcher.filters.state import State
from man_project_2023.utils.schemas.api_schemas import BaseGig, BaseUser
from man_project_2023.telegram_bot.api.utils_schemas import StateStructure
from aiogram.dispatcher.storage import FSMContext


utils = Utils()

class CurrentState:

    def __init__(self, state: FSMContext = None, keyboard_class = None, state_class = None):
        self.state = state
        self.keyboard_class = keyboard_class
        self.state_class = state_class

    async def set_state(self, state: FSMContext):
        self.state = state

    async def update_classes(self, keyboard_class, state_class):
        self.keyboard_class = keyboard_class
        self.state_class = state_class

    async def state_attr(self):
        return getattr(self.state_class, await self.get_name())

    async def get_state(self) -> dict:
        state: str = await self.state.get_state()
        if state is not None:
            data: list = state.split(":")
            return {
                "name": data[-1],
                "group": data[0]
            }
        return None

    async def get_name(self):
        state = await self.get_state()
        if state is not None:
            return state["name"]
        return None

    async def get_group(self):
        state = await self.get_state()
        if state is not None:
            return state["group"]
        return None

    async def get_state_class(self):
        return self.state_class()

    async def get_class(self):
        return self.keyboard_class()

    async def add_reply_markup(self, buttons_list: list,
                               reply_markup: InlineKeyboardMarkup = None):

        for i in reply_markup.inline_keyboard:
            row_data: list = []
            for j in i:
                row_data.append(dict(j))
            buttons_list.append(row_data)
        return buttons_list

    async def get_buttons(self, mark_current: bool = True,
                          reply_markup: InlineKeyboardMarkup = None):
        keyboard = vars(await self.get_class())

        buttons_list: list = []
        for i, v in keyboard.items():
            if "callback" not in i:
                buttons_list.append([{"text": f"✅ {v}" if mark_current and await self.get_name() == i else v,
                                      "callback_data": keyboard[i + "_callback"]}])

        return await self.add_reply_markup(buttons_list=buttons_list,
                                           reply_markup=reply_markup) if reply_markup is not None else buttons_list

    async def get_placeholder(self, required_state: State = None):
        buttons = vars(await self.get_class())
        state = await self.get_name()
        callback: str = "placeholder_callback"

        placeholder: list = {"text": f"✅ {buttons[state] if required_state is None else buttons[required_state._state]} ▼",
                            "callback_data": callback}

        return placeholder

    async def state_photo(self, image: str):
        path: str = f"img/states_images/{image}.png"
        photo = open(path, "rb")
        return photo




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




class ListMenuManager:

    def __init__(self):
        self.elements_list: list = []

    async def add(self, message: Message) -> None:
        if element := message.text:
            await message.delete()
            if element in self.elements_list:
                return ListMenu.keyboard(elements_list=self.elements_list,
                                         with_next=True)
            self.elements_list.append(element)
            return ListMenu.keyboard(elements_list=self.elements_list,
                                     with_next=True)

    async def remove(self, callback: CallbackQuery, state: FSMContext) -> None:
        element = callback.data[:callback.data.rindex("_list_menu")]
        if element in self.elements_list:
            self.elements_list.remove(element)
            await callback.message.edit_reply_markup(
                reply_markup=ListMenu.keyboard(
                    elements_list=self.elements_list,
                    with_skip=True if not self.elements_list else False,
                    with_next=True if self.elements_list else False
                )
            )




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
        return self.message

    async def send_default(self, current_state: CurrentState, text: str,
                           image: str = "", reply_markup = None):
        self.current_state = current_state
        chat_id: int = self.current_state.state.chat
        if image:
            photo = await self.current_state.state_photo(image=image)
            self.message = await bot.send_photo(chat_id=chat_id,
                                                caption=text,
                                                photo=photo,
                                                reply_markup=reply_markup,
                                                parse_mode="Markdown")

            return self.message
        await bot.send_message(chat_id=chat_id,
                               text=text,
                               reply_markup=reply_markup,
                               parse_mode="Markdown")

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
        await self.delete_context_messages()
        self.previous_state = None
        self.reset_data()


    def reset_data(self):
        self.is_used = False


class Marketplace:
    """
    Класс который обеспечивает работу системы поиска проекта, также все функции связанные с собственными объявлениями пользователя
    Функции фильтров и прочего
    """

    async def get_user_gigs(self, telegram_id: int):
        response = await UserAPI.get_user(telegram_id=telegram_id)
        # if response.success:

