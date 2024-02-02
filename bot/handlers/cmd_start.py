from typing import TYPE_CHECKING

from _redis_funcs import save_msg_data_to_redis
from _reply_markups import START_KEYBOARD
from handlers._messages import cmd_start_reply_text

if TYPE_CHECKING:
    from aiogram import types
    from aiogram.fsm.context import FSMContext


async def cmd_start(msg: "types.Message", state: "FSMContext") -> None:
    message = await msg.answer(text=cmd_start_reply_text, reply_markup=START_KEYBOARD)

    await save_msg_data_to_redis("start", message)

    await state.clear()
