from typing import TYPE_CHECKING

from db import db_manager
from ._messages import get_msg_by_cards

if TYPE_CHECKING:
    from aiogram import types
    from aiogram.fsm.context import FSMContext


async def get_cards(msg: "types.Message", state: "FSMContext") -> None:
    cards = db_manager.get_all_cards(msg.from_user.id)
    message = get_msg_by_cards(cards)

    await msg.answer(text=message)
