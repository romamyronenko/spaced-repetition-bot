from typing import TYPE_CHECKING

from _message_editors import delete_reply_markup_start_message
from db import db_manager
from _reply_markups import get_learn_keyboard

if TYPE_CHECKING:
    from aiogram import types
    from aiogram.fsm.context import FSMContext


class Learn:
    @staticmethod
    async def remember_callback(
            callback: "types.CallbackQuery", state: "FSMContext"
    ) -> None:
        await callback.message.answer(text=callback.data)
        card_id = callback.data.split(" ")[-1]
        db_manager.update_remember(card_id)
        await Learn.learn_callback(callback, state)

    @staticmethod
    async def forget_callback(callback: "types.CallbackQuery", state: "FSMContext") -> None:
        await callback.message.answer(text=callback.data)
        card_id = callback.data.split(" ")[-1]
        db_manager.update_forget(card_id)
        await Learn.learn_callback(callback, state)

    @staticmethod
    async def learn_callback(callback: "types.CallbackQuery", state: "FSMContext") -> None:
        card = db_manager.get_card_to_check(callback.from_user.id)
        if card is not None:
            await callback.message.answer(
                text=f'{card.front_side}\n\n<span class="tg-spoiler">{card.back_side}</span>',
                parse_mode="html",
                reply_markup=get_learn_keyboard(card.id),
            )
            await delete_reply_markup_start_message(callback.bot, callback.from_user.id)
        else:
            await callback.answer(text="На сьогодні ви вже повторили всі слова.")
