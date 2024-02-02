CMD_START_REPLY_TEXT = "Привіт, я - бот для запам'ятовування."
ADD_CALLBACK_REPLY_TEXT = "Введіть дані в наступному форматі:\nслово - значення"
ADD_SEPARATOR = " - "
WRONG_ADD_MESSAGE_FORMAT_MSG = "Невірний формат"
NO_CARDS_TO_LEARN_MSG = "На сьогодні ви вже повторили всі слова."


def get_msg_by_cards(cards):
    if cards:
        msg = "\n".join([str(card) for card in cards])
    else:
        msg = "У вас немає карток."

    return msg


def get_learn_message(card):
    return f'{card.front_side}\n\n<span class="tg-spoiler">{card.back_side}</span>'
