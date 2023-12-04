from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    start = State()
    add_card = State()
    add_back_side = State()
    learn = State()
