from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

ADD_IS_DONE_KEYBAORD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Готово!")]], resize_keyboard=True
)
START_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Додати слова!"),
            KeyboardButton(text="Вчити!"),
        ]
    ],
    resize_keyboard=True,
)


def get_learn_keyboard(card_id: int) -> "InlineKeyboardMarkup":
    """
    Keyboard for learn message. Has two buttons for 'remember' and 'forget' actions
    :param card_id: id of the card
    :return:
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✔️", callback_data=f"remember {card_id}"),
                InlineKeyboardButton(text="❌", callback_data="forget"),
            ]
        ]
    )
