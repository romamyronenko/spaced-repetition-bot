from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ADD_IS_DONE_KEYBAORD = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Готово!", callback_data="done")]]
)
START_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Додати слова", callback_data="add"),
            InlineKeyboardButton(text="Вчити!", callback_data="learn"),
        ]
    ]
)
