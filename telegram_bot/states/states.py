from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.storage import FSMContext
from aiogram.types import Message

class MainMenuStates(StatesGroup):
    start_menu = State()

class MarketplaceStates(StatesGroup):
    search_input = State()
    gigs_list = State()

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

class FiltersStates(StatesGroup):
    filters = State()
    time_filter = State()
    location_filter = State()
    tags_filter =State()

