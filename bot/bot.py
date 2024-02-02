import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

import handlers
from _form import Form
from handlers import (
    remember_callback,
    forget_callback,
    learn_callback,
    add_callback,
    add_card_state,
    done_callback,
)

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILENAME = "log.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format=LOG_FORMAT)

TOKEN_API = os.getenv("TOKEN_API")
router = Router()

msg_handlers = (
    (handlers.cmd_start, CommandStart()),
    (handlers.get_cards, Command("get_cards")),
    (add_card_state, Form.add_card),
)

callback_handlers = (
    (remember_callback, F.data.startswith("remember")),
    (forget_callback, F.data.startswith("forget")),
    (learn_callback, F.data == "learn"),
    (done_callback, F.data == "done"),
    (add_callback, F.data == "add"),
)

for func, template in msg_handlers:
    router.message.register(func, template)

for func, template in callback_handlers:
    router.callback_query.register(func, template)


async def main_async() -> None:
    logging.info("starting...")
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(router)
    bot = Bot(token=TOKEN_API)
    await bot.set_my_commands(
        [
            types.BotCommand(command="start", description="Запустити бота"),
            types.BotCommand(command="get_cards", description="Показати всі картки"),
        ]
    )
    await dp.start_polling(bot)
    logging.info("bot started")


if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except Exception as e:
        logging.error(str(e))
        logging.info("bot stopped")
        raise e
