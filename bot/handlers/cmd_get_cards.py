from typing import TYPE_CHECKING

from db import db_manager

if TYPE_CHECKING:
    from aiogram import types
    from aiogram.fsm.context import FSMContext


async def get_cards(msg: "types.Message", state: "FSMContext") -> None:
    cards = db_manager.get_all_cards(msg.from_user.id)
    if cards:
        message = "\n".join([str(card) for card in cards])
    else:
        message = "У вас немає карток."
    await msg.answer(text=message)
