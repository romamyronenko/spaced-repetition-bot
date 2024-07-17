from typing import TYPE_CHECKING

import handlers
from _form import Form
from db import db_manager
from ._messages import (
    ADD_CALLBACK_REPLY_TEXT,
    ADD_SEPARATOR,
    WRONG_ADD_MESSAGE_FORMAT_MSG,
)
from ._redis_funcs import save_msg_data_to_redis
from ._reply_markups import ADD_IS_DONE_KEYBAORD

if TYPE_CHECKING:
    from aiogram import types
    from aiogram.fsm.context import FSMContext


async def done_callback(message: "types.Message", state: "FSMContext") -> None:
    await state.clear()
    await handlers.cmd_start(message, state)


async def add_callback(message: "types.Message", state: "FSMContext") -> None:
    msg = await message.answer(
        text=ADD_CALLBACK_REPLY_TEXT, reply_markup=ADD_IS_DONE_KEYBAORD
    )
    await save_msg_data_to_redis("add", msg)
    await state.set_state(Form.add_card)


async def add_card_state(msg: "types.Message", state: "FSMContext") -> None:
    message = msg.text
    print(msg)

    if ADD_SEPARATOR in message:
        front, back = message.split(ADD_SEPARATOR)
        db_manager.add_card(front, back, msg.from_user.id)
        await msg.answer(text="Додано!")

    else:
        await msg.answer(WRONG_ADD_MESSAGE_FORMAT_MSG)
        await state.clear()
