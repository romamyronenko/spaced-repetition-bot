from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiohttp import web

from db import engine
from db.schema import Base
from db_funcs import get_all_cards, add_card_to_db, get_cards_to_check
from form import Form
from ngrok import get_url
from tk import TOKEN_API

bot = Bot(token=TOKEN_API)
Bot.set_current(bot)

dp = Dispatcher(bot, storage=MemoryStorage())
app = web.Application()

webhook_path = f"/{TOKEN_API}"

temp_user_data = {}


async def set_webhook():
    webhook_uri = f"{get_url()}{webhook_path}"
    await bot.set_webhook(webhook_uri)


async def on_startup(_):
    await set_webhook()


@dp.message_handler(commands=["start", "help"], state="*")
async def cmd_start_help(msg: types.Message, state: FSMContext) -> None:
    reply_text = "Hello😃"
    await msg.answer(text=reply_text)
    await state.set_state(Form.start)


@dp.message_handler(commands=["add_card"], state="*")
async def add_card(msg: types.Message, state: FSMContext) -> None:
    reply_text = "To add a card write the text for front size."
    await msg.answer(text=reply_text)
    await state.set_state(Form.add_card)


@dp.message_handler(state=Form.add_card)
async def add_card_state(msg: types.Message, state: FSMContext) -> None:
    message = msg.text
    front, back = None, None

    sep = '\n'
    if sep in message:
        front, back = message.split(sep)
        add_card_to_db(front, back, msg.from_user.id)
        await state.set_state(Form.start)
        await msg.answer(f"{back} | {front}")
    else:
        front = message
        global temp_user_data
        temp_user_data[msg.from_user.id] = front
        await msg.answer(f"{back} | {front}")
        await state.set_state(Form.add_back_side)


@dp.message_handler(state=Form.add_back_side)
async def add_back_side(msg: types.Message, state: FSMContext) -> None:
    global temp_user_data
    front = temp_user_data.pop(msg.from_user.id)
    add_card_to_db(front, msg.text, msg.from_user.id)
    await msg.answer(f"{msg.text} | {front}")
    await state.set_state(Form.start)


@dp.message_handler(commands=["get_cards"], state="*")
async def get_cards(msg: types.Message, state: FSMContext) -> None:
    # await msg.answer(text=str(get_all_cards(msg.from_user.id)))
    await msg.answer("\n".join([str(card) for card in get_all_cards(msg.from_user.id)]))


@dp.message_handler(commands=["check"], state="*")
async def check(msg: types.Message, state: FSMContext) -> None:
    user_id = msg.from_user.id
    _temp = temp_user_data.get(user_id)
    if isinstance(_temp, list):
        temp_user_data[user_id] = get_cards_to_check(user_id)


async def handle_webhook(request):
    url = str(request.url)
    index = url.rfind("/")
    token = url[index + 1:]

    if token == TOKEN_API:
        request_data = await request.json()
        update = types.Update(**request_data)
        await dp.process_update(update)

        return web.Response()

    else:
        return web.Response(status=403)


app.router.add_post(f"/{TOKEN_API}", handle_webhook)
if __name__ == "__main__":
    app.on_startup.append(on_startup)
    Base.metadata.create_all(engine)

    web.run_app(app, host="0.0.0.0", port=8080)
