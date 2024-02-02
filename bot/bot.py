import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

import handlers
from _form import Form
from handlers import Learn
from handlers.scenario_add import Add

log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
log_filename = "log.log"
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format=log_format)

TOKEN_API = os.getenv("TOKEN_API")
router = Router()


def main() -> None:
    logging.info("starting...")
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(router)
    bot = Bot(token=TOKEN_API)
    asyncio.run(dp.start_polling(bot))
    logging.info("bot started")


msg_handlers = (
    (handlers.cmd_start, CommandStart()),
    (handlers.get_cards, Command("get_cards")),
    (Add.add_card_state, Form.add_card),
)

callback_handlers = (
    (Learn.remember_callback, F.data.startswith("remember")),
    (Learn.forget_callback, F.data.startswith("forget")),
    (Learn.learn_callback, F.data == "learn"),
    (Add.done_callback, F.data == "done"),
    (Add.add_callback, F.data == "add"),
)

for func, template in msg_handlers:
    router.message.register(func, template)

for func, template in callback_handlers:
    router.callback_query.register(func, template)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(str(e))
        logging.info("bot stopped")
        raise e
