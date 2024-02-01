import asyncio
import logging
import os
from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

from _message_editors import delete_reply_markup_start_message, update_text_saved_add_message, \
    delete_reply_markup_add_message
from _redis_funcs import save_msg_data_to_redis
from db import db_manager
from _form import Form
import handlers
from reply_markups import ADD_IS_DONE_KEYBAORD, get_learn_keyboard

if TYPE_CHECKING:
    from aiogram import types
    from aiogram.fsm.context import FSMContext

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_filename = "log.log"
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=log_format)

TOKEN_API = os.getenv("TOKEN_API")
router = Router()


class Learn:
    @staticmethod
    async def remember_callback(
            callback: "types.CallbackQuery", state: "FSMContext"
    ) -> None:
        await callback.message.answer(text=callback.data)
        card_id = callback.data.split(" ")[-1]
        db_manager.update_remember(card_id)
        await Learn.learn_callback(callback, state)

    @staticmethod
    async def forget_callback(callback: "types.CallbackQuery", state: "FSMContext") -> None:
        await callback.message.answer(text=callback.data)
        card_id = callback.data.split(" ")[-1]
        db_manager.update_forget(card_id)
        await Learn.learn_callback(callback, state)

    @staticmethod
    async def learn_callback(callback: "types.CallbackQuery", _: "FSMContext") -> None:
        card = db_manager.get_card_to_check(callback.from_user.id)
        if card is not None:
            await callback.message.answer(
                text=f'{card.front_side}\n\n<span class="tg-spoiler">{card.back_side}</span>',
                parse_mode="html",
                reply_markup=get_learn_keyboard(card.id),
            )
            await delete_reply_markup_start_message(callback.bot, callback.from_user.id)
        else:
            await callback.answer(text="На сьогодні ви вже повторили всі слова.")


class Add:
    @staticmethod
    async def done_callback(callback: "types.CallbackQuery", state: "FSMContext") -> None:
        await state.clear()
        await delete_reply_markup_add_message(callback.bot, callback.from_user.id)
        await handlers.cmd_start(callback.message, state)

    @staticmethod
    async def add_callback(callback: "types.CallbackQuery", state: "FSMContext") -> None:
        await delete_reply_markup_start_message(callback.bot, callback.from_user.id)
        reply_text = "Введіть дані в наступному форматі:\nслово - значення"
        msg = await callback.message.answer(
            text=reply_text, reply_markup=ADD_IS_DONE_KEYBAORD
        )
        await save_msg_data_to_redis("add", msg)
        await state.set_state(Form.add_card)

    @staticmethod
    async def add_card_state(msg: "types.Message", state: "FSMContext") -> None:
        message = msg.text

        sep = " - "
        if sep in message:
            bot = msg.bot
            front, back = message.split(sep)
            await update_text_saved_add_message(bot, msg.from_user.id, message)
            db_manager.add_card(front, back, msg.from_user.id)
            await msg.delete()

        else:
            await msg.answer("Невірний формат")
            await state.clear()


def main() -> None:
    logging.info("starting...")
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(router)
    bot = Bot(token=TOKEN_API)
    asyncio.run(dp.start_polling(bot))
    logging.info("bot started")


router.message.register(handlers.cmd_start, CommandStart())
router.message.register(handlers.get_cards, Command("get_cards"))
router.message.register(Add.add_card_state, Form.add_card)

router.callback_query.register(Learn.remember_callback, F.data.startswith("remember"))
router.callback_query.register(Learn.forget_callback, F.data.startswith("forget"))
router.callback_query.register(Learn.learn_callback, F.data == "learn")
router.callback_query.register(Add.done_callback, F.data == "done")
router.callback_query.register(Add.add_callback, F.data == "add")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(str(e))
        logging.info("bot stopped")
        raise e
