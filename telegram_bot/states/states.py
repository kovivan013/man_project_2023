from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message
from man_project_2023.telegram_bot.keyboards.keyboards import DropdownMenu

class CurrentState:

    def __init__(self, state: FSMContext, keyboard_class = None, state_class = None):
        self.state = state
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

    async def get_buttons(self, mark_current: bool = True):
        keyboard = vars(await self.get_class())

        buttons_list: list = []
        for i, v in keyboard.items():
            if "callback" not in i:
                buttons_list.append([{"text": f"✅ {v}" if mark_current and await self.get_name() == i else v,
                                      "callback_data": keyboard[i + "_callback"]}])

        return buttons_list

    async def get_placeholder(self, required_state: State = None):
        buttons = vars(await self.get_class())
        state = await self.get_name()
        callback: str = "placeholder_callback"

        return {"text": f"✅ {buttons[state] if required_state is None else buttons[required_state._state]} ▼",
                "callback_data": callback}

    async def state_photo(self, image: str):
        path: str = f"img/states_images/{image}.png"
        photo = open(path, "rb")
        return photo




class ProfileStates(StatesGroup):
    info_about = State()
    gigs = State()
    username = State()
    description = State()
    select_menu = State()

    # @classmethod
    # async def state_image(cls, path: str = "img/states_images/",
    #                       mode: str = "rb"):
    #     return open(path + "dashboard_profile", mode)


    # tasks = State()
    # in states (editing etc.)


