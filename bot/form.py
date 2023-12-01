from aiogram.dispatcher.filters.state import StatesGroup, State


class Form(StatesGroup):
    start = State()
    add_card = State()
    add_back_side = State()
    learn = State()
