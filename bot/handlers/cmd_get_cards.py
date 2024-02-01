from aiogram import types
from aiogram.fsm.context import FSMContext

from db import db_manager


async def get_cards(msg: "types.Message", _: "FSMContext") -> None:
    cards = db_manager.get_all_cards(msg.from_user.id)
    if cards:
        message = "\n".join([str(card) for card in cards])
    else:
        message = "У вас немає карток."
    await msg.answer(text=message)
