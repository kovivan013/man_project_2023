from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message
from man_project_2023.telegram_bot.keyboards.keyboards import DropdownMenu, InlineKeyboardMarkup

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




class ProfileStates(StatesGroup):
    info_about = State()
    gigs = State()
    select_menu = State()
    edit_menu = State()

class UpdateDescriptionStates(StatesGroup):
    username = State()
    description = State()
    input_username = State()
    input_description = State()
    confirm_username = State()
    backward_description = State()
    confirm_description = State()

    # @classmethod
    # async def state_image(cls, path: str = "img/states_images/",
    #                       mode: str = "rb"):
    #     return open(path + "dashboard_profile", mode)


    # tasks = State()
    # in states (editing etc.)


