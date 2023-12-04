from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from bot import cmd_start_help
from keyboards import START_KEYBOARD
from tests.utils import TEST_USER, TEST_USER_CHAT


@pytest.mark.asyncio
async def test_start_handler(storage, bot):
    message = AsyncMock()
    state = FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id),
    )
    await cmd_start_help(message, state=state)

    message.answer.assert_called_with(
        text="Привіт, я - бот для запам'ятовування.",
        reply_markup=START_KEYBOARD,
    )
