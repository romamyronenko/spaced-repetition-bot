from typing import TYPE_CHECKING

from ._messages import CMD_START_REPLY_TEXT
from ._redis_funcs import save_msg_data_to_redis
from ._reply_markups import START_KEYBOARD

if TYPE_CHECKING:
    from aiogram import types
    from aiogram.fsm.context import FSMContext


async def cmd_start(msg: "types.Message", state: "FSMContext") -> None:
    message = await msg.answer(text=CMD_START_REPLY_TEXT, reply_markup=START_KEYBOARD)

    await save_msg_data_to_redis("start", message)

    await state.clear()
