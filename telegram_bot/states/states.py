from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message
from man_project_2023.telegram_bot.keyboards.keyboards import DropdownMenu, InlineKeyboardMarkup

class MainMenuStates(StatesGroup):
    start_menu = State()

class ProfileStates(StatesGroup):
    info_about = State()
    gigs = State()
    select_menu = State()
    edit_menu = State()

class UpdateDescriptionStates(StatesGroup):
    description = State()
    input_description = State()
    backward_description = State()
    confirm_description = State()

class UpdateUsernameStates(StatesGroup):
    username = State()
    check_username = State()
    confirm_username = State()
    backward_username = State()

class CreateGigStates(StatesGroup):
    name = State()
    description = State()
    photo = State()
    location = State()
    date = State()
    tags = State()
    check_data = State()
    backward = State()

    # @classmethod
    # async def state_image(cls, path: str = "img/states_images/",
    #                       mode: str = "rb"):
    #     return open(path + "dashboard_profile", mode)


    # tasks = State()
    # in states (editing etc.)


