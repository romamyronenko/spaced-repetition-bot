from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from db import db_manager
from form import Form
from keyboards import ADD_IS_DONE_KEYBAORD, START_KEYBOARD
from ngrok import get_url
from tk import TOKEN_API

router = Router()
webhook_path = f"/{TOKEN_API}"

saved_user_msg_id = {}


@router.callback_query(F.data.startswith("remember"))
async def remember_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=callback.data)
    card_id = callback.data.split(" ")[-1]
    db_manager.update_remember(card_id)
    await learn_callback(callback, state)


@router.callback_query(F.data.startswith("forget"))
async def forget_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    await callback.message.answer(text=callback.data)


@router.callback_query(F.data == "learn")
async def learn_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    # await callback.message.answer(text=f'{get_card_to_check(callback.from_user.id)}')
    card = db_manager.get_cards_to_check(callback.from_user.id)[0] or None
    if card is not None:

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✔️", callback_data=f"remember {card.id}"
                    ),
                    InlineKeyboardButton(text="❌", callback_data="forget"),
                ]
            ]
        )
        await callback.message.answer(
            text=f'{card.front_side}\n\n<span class="tg-spoiler">{card.back_side}</span>',
            parse_mode="html",
            reply_markup=kb,
        )
    else:
        await callback.message.answer(text="На сьогодні ви вже повторили всі слова.")
        await cmd_start_help(callback.message, state)


@router.callback_query(F.data == "done")
async def done_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await saved_user_msg_id[callback.from_user.id].delete_reply_markup()
    await cmd_start_help(callback.message, state)


@router.callback_query(F.data == "add")
async def add_callback(callback: types.CallbackQuery, state: FSMContext) -> None:
    reply_text = "Введіть дані в наступному форматі:\nслово - значення"
    msg = await callback.message.answer(
        text=reply_text, reply_markup=ADD_IS_DONE_KEYBAORD
    )
    saved_user_msg_id[callback.from_user.id] = msg
    await state.set_state(Form.add_card)


@router.message(CommandStart())
async def cmd_start_help(msg: types.Message, state: FSMContext) -> None:
    reply_text = "Привіт, я - бот для запам'ятовування."

    await msg.answer(text=reply_text, reply_markup=START_KEYBOARD)
    await state.clear()


@router.message(Command("add_card"))
async def add_card(msg: types.Message, state: FSMContext) -> None:
    reply_text = "To add a card write the text for front size."
    await msg.answer(text=reply_text)
    await state.set_state(Form.add_card)


@router.message(Form.add_card)
async def add_card_state(msg: types.Message, state: FSMContext) -> None:
    message = msg.text
    # front, back = None, None

    sep = " - "
    if sep in message:
        front, back = message.split(sep)
        db_manager.add_card_to_db(front, back, msg.from_user.id)
        saved_msg = saved_user_msg_id[msg.from_user.id]
        saved_user_msg_id[msg.from_user.id] = await saved_msg.edit_text(
            text=f"{saved_msg.text}\n{front} - {back}",
            reply_markup=ADD_IS_DONE_KEYBAORD,
        )
        await msg.delete()

    else:
        await msg.answer("Невірний формат")
        await state.clear()


@router.message(Command("get_cards"))
async def get_cards(msg: types.Message, state: FSMContext) -> None:
    await msg.answer(
        "\n".join([str(card) for card in db_manager.get_all_cards(msg.from_user.id)])
    )


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


if __name__ == "__main__":
    main()
