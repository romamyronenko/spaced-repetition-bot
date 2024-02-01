from aiogram import types
from aiogram.fsm.context import FSMContext

from _redis_funcs import save_msg_data_to_redis
from reply_markups import START_KEYBOARD


async def cmd_start(msg: "types.Message", state: "FSMContext") -> None:
    reply_text = "Привіт, я - бот для запам'ятовування."

    message = await msg.answer(text=reply_text, reply_markup=START_KEYBOARD)

    await save_msg_data_to_redis("start", message)

    await state.clear()
