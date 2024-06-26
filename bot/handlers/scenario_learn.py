from typing import TYPE_CHECKING

from db import db_manager
from . import cmd_start
from ._message_editors import delete_reply_markup_start_message
from ._messages import get_learn_message, NO_CARDS_TO_LEARN_MSG
from ._reply_markups import get_learn_keyboard

if TYPE_CHECKING:
    from aiogram import types
    from aiogram.fsm.context import FSMContext


async def remember_callback(
    callback: "types.CallbackQuery", state: "FSMContext"
) -> None:
    card_id = _get_card_id_from_callback(callback)
    db_manager.update_remember(card_id)

    await learn_callback(callback, state)


async def forget_callback(callback: "types.CallbackQuery", state: "FSMContext") -> None:
    card_id = _get_card_id_from_callback(callback)
    db_manager.update_forget(card_id)

    await learn_callback(callback, state)


async def learn_callback(callback: "types.CallbackQuery", state: "FSMContext") -> None:
    card = db_manager.get_card_to_check(callback.from_user.id)

    if card is not None:
        await _send_card_message(callback, card)
        await delete_reply_markup_start_message(callback.bot, callback.from_user.id)

    else:
        await callback.answer(text=NO_CARDS_TO_LEARN_MSG)
        await cmd_start(callback.message, state)


async def _send_card_message(callback, card):
    await callback.message.answer(
        text=get_learn_message(card),
        parse_mode="html",
        reply_markup=get_learn_keyboard(card.id),
    )


def _get_card_id_from_callback(callback):
    return callback.data.split(" ")[-1]
