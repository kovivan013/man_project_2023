from aiogram.dispatcher.filters.state import State, StatesGroup

class ProfileStates(StatesGroup):
    info_about = State()
    my_gigs = State()
    # tasks = State()
    # in states (editing etc.)