from typing import TYPE_CHECKING

import handlers
from _form import Form
from db import db_manager
from ._message_editors import (
    delete_reply_markup_add_message,
    delete_reply_markup_start_message,
    update_text_saved_add_message,
)
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


async def done_callback(callback: "types.CallbackQuery", state: "FSMContext") -> None:
    await state.clear()
    await delete_reply_markup_add_message(callback.bot, callback.from_user.id)
    await handlers.cmd_start(callback.message, state)


async def add_callback(callback: "types.CallbackQuery", state: "FSMContext") -> None:
    await delete_reply_markup_start_message(callback.bot, callback.from_user.id)
    msg = await callback.message.answer(
        text=ADD_CALLBACK_REPLY_TEXT, reply_markup=ADD_IS_DONE_KEYBAORD
    )
    await save_msg_data_to_redis("add", msg)
    await state.set_state(Form.add_card)


async def add_card_state(msg: "types.Message", state: "FSMContext") -> None:
    message = msg.text

    if ADD_SEPARATOR in message:
        bot = msg.bot
        front, back = message.split(ADD_SEPARATOR)
        await update_text_saved_add_message(bot, msg.from_user.id, message)
        db_manager.add_card(front, back, msg.from_user.id)
        await msg.delete()

    else:
        await msg.answer(WRONG_ADD_MESSAGE_FORMAT_MSG)
        await state.clear()
