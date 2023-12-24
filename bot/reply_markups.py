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


def get_learn_keyboard(card_id):
    InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✔️", callback_data=f"remember {card_id}"
                ),
                InlineKeyboardButton(text="❌", callback_data="forget"),
            ]
        ]
    )
