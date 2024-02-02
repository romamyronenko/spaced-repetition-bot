import logging

from aiogram.exceptions import TelegramBadRequest

from _redis_funcs import get_msg_data_from_redis, save_msg_data_to_redis
from _reply_markups import ADD_IS_DONE_KEYBAORD


# TODO: add type annotations
async def delete_reply_markup_start_message(bot, user_id):
    msg_data = await get_msg_data_from_redis("start", user_id)
    msg_id = msg_data["message_id"]
    chat_id = msg_data["chat_id"]
    logging.debug(f"delete message {msg_id} from chat {chat_id}")
    try:
        await bot.edit_message_reply_markup(chat_id, msg_id)
    except TelegramBadRequest as e:
        logging.debug(str(e))


async def update_text_saved_add_message(bot, user_id, text_to_add):
    msg_data = await get_msg_data_from_redis("add", user_id)
    msg_id = msg_data["message_id"]
    chat_id = msg_data["chat_id"]
    text = msg_data["text"]
    try:
        msg = await bot.edit_message_text(
            text=f"{text}\n{text_to_add}",
            chat_id=chat_id,
            message_id=msg_id,
            reply_markup=ADD_IS_DONE_KEYBAORD,
        )

        await save_msg_data_to_redis("add", msg)
    except TelegramBadRequest as e:
        logging.debug(str(e))


async def delete_reply_markup_add_message(bot, user_id):
    msg_data = await get_msg_data_from_redis("add", user_id)
    msg_id = msg_data["message_id"]
    chat_id = msg_data["chat_id"]
    logging.debug(f"delete message {msg_id} from chat {chat_id}")
    try:
        await bot.edit_message_reply_markup(chat_id, msg_id)
    except TelegramBadRequest as e:
        logging.debug(str(e))
