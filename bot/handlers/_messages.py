cmd_start_reply_text = "Привіт, я - бот для запам'ятовування."
add_callback_reply_text = "Введіть дані в наступному форматі:\nслово - значення"
add_separator = " - "
wrong_add_message_format_msg = "Невірний формат"
no_cards_to_learn_msg = "На сьогодні ви вже повторили всі слова."


def get_msg_by_cards(cards):
    if cards:
        msg = "\n".join([str(card) for card in cards])
    else:
        msg = "У вас немає карток."

    return msg


def get_learn_message(card):
    return f'{card.front_side}\n\n<span class="tg-spoiler">{card.back_side}</span>'
