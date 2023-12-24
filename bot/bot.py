from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from db import db_manager
from form import Form
from ngrok import get_url
from reply_markups import ADD_IS_DONE_KEYBAORD, START_KEYBOARD, get_learn_keyboard
from tk import TOKEN_API

router = Router()
webhook_path = f"/{TOKEN_API}"

saved_user_msg = {}


async def remember_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=callback.data)
    card_id = callback.data.split(" ")[-1]
    db_manager.update_remember(card_id)
    await learn_callback(callback, state)


async def forget_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=callback.data)


async def learn_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    cards = db_manager.get_cards_to_check(callback.from_user.id)
    card = cards[0] if cards else None
    if card is not None:

        await callback.message.answer(
            text=f'{card.front_side}\n\n<span class="tg-spoiler">{card.back_side}</span>',
            parse_mode="html",
            reply_markup=get_learn_keyboard(card.id),
        )
    else:
        await callback.message.answer(text="На сьогодні ви вже повторили всі слова.")
        await cmd_start(callback.message, state)

async def done_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await saved_user_msg[callback.from_user.id].delete_reply_markup()
    await cmd_start(callback.message, state)


async def add_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    await saved_user_msg[callback.from_user.id].delete_reply_markup()
    reply_text = "Введіть дані в наступному форматі:\nслово - значення"
    msg = await callback.message.answer(
        text=reply_text, reply_markup=ADD_IS_DONE_KEYBAORD
    )
    saved_user_msg[callback.from_user.id] = msg
    await state.set_state(Form.add_card)


async def cmd_start(msg: types.Message, state: FSMContext) -> None:
    reply_text = "Привіт, я - бот для запам'ятовування."

    saved_user_msg[msg.from_user.id] = await msg.answer(
        text=reply_text, reply_markup=START_KEYBOARD
    )

    await state.clear()


async def add_card_state(msg: types.Message, state: FSMContext) -> None:
    message = msg.text

    sep = " - "
    if sep in message:
        front, back = message.split(sep)
        db_manager.add_card(front, back, msg.from_user.id)
        saved_msg = saved_user_msg[msg.from_user.id]
        saved_user_msg[msg.from_user.id] = await saved_msg.edit_text(
            text=f"{saved_msg.text}\n{front} - {back}",
            reply_markup=ADD_IS_DONE_KEYBAORD,
        )
        await msg.delete()

    else:
        await msg.answer("Невірний формат")
        await state.clear()


async def get_cards(msg: types.Message, state: FSMContext) -> None:
    cards = db_manager.get_all_cards(msg.from_user.id)
    if cards:
        message = "\n".join([str(card) for card in cards])
    else:
        message = "У вас немає карток."
    await msg.answer(text=message)


async def set_webhook(bot):
    webhook_uri = f"{get_url()}{webhook_path}"
    await bot.set_webhook(webhook_uri)


async def on_startup(bot):
    await set_webhook(bot)


def main() -> None:
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(router)
    dp.startup.register(on_startup)
    bot = Bot(token=TOKEN_API)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=webhook_path)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host="0.0.0.0", port=8080)


router.message.register(cmd_start, CommandStart())
router.message.register(get_cards, Command("get_cards"))
router.message.register(add_card_state, Form.add_card)

router.callback_query.register(remember_callback, F.data.startswith("remember"))
router.callback_query.register(forget_callback, F.data.startswith("forget"))
router.callback_query.register(learn_callback, F.data == "learn")
router.callback_query.register(done_callback, F.data == "done")
router.callback_query.register(add_callback, F.data == "add")

if __name__ == "__main__":
    main()