from typing import TYPE_CHECKING

from db import db_manager

if TYPE_CHECKING:
    from aiogram import types
    from aiogram.fsm.context import FSMContext


async def delete_cards(msg: "types.Message", state: "FSMContext") -> None:
    try:
        arguments = msg.text.split(" ")[1:]

        db_manager.remove_cards(msg.from_user.id, arguments)

        await msg.answer(text="Картки видалено!")
    except Exception as _:
        await msg.answer(text="щось пішло не так...")
