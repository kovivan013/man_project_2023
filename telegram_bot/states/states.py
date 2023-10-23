from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from pydantic import BaseModel


class CurrentState:

    def __init__(self, state: FSMContext, keyboard_class = None):
        self.state = state
        self.keyboard_class = keyboard_class

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

    async def get_class(self):
        return self.keyboard_class()

    async def get_buttons(self, mark_current: bool = True):
        keyboard = vars(await self.get_class())

        buttons_list: list = []
        for i, v in keyboard.items():
            if "callback" not in i:
                buttons_list.append([{"text": f"✅ {v}" if mark_current else v,
                                      "callback_data": keyboard[i + "_callback"]}])

        return buttons_list

    async def get_placeholder(self):
        buttons = vars(await self.get_class())
        state = await self.get_name()

        return {"text": f"✅ {buttons[state]} ▼", "callback_data": buttons[state + "_callback"]}


class ProfileStates(StatesGroup):
    info_about = State()
    gigs = State()
    # tasks = State()
    # in states (editing etc.)

