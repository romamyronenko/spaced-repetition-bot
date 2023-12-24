from unittest import mock
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import create_engine

from bot import cmd_start, get_cards, add_callback, saved_user_msg, add_card_state
from form import Form
from reply_markups import START_KEYBOARD, ADD_IS_DONE_KEYBAORD
from tests.utils import TEST_USER

engine = create_engine("sqlite://")


@pytest.mark.asyncio
async def test_start_handler(state, message):
    assert not saved_user_msg
    await cmd_start(message, state=state)

    message.answer.assert_called_with(
        text="Привіт, я - бот для запам'ятовування.",
        reply_markup=START_KEYBOARD,
    )
    assert saved_user_msg


@pytest.mark.asyncio
async def test_get_cards(state, message, db_manager):
    for front, back in (("1", "2"), ("front", "back")):
        db_manager.add_card(front, back, TEST_USER.id)

    with mock.patch("bot.db_manager", new=db_manager):
        await get_cards(message, state)

    message.answer.assert_called_with(
        text="1 - 2\nfront - back",
    )


@pytest.mark.asyncio
async def test_get_cards_when_empty(state, message, db_manager):
    with mock.patch("bot.db_manager", new=db_manager):
        await get_cards(message, state)

    message.answer.assert_called_with(
        text="У вас немає карток.",
    )


@pytest.mark.asyncio
async def test_add_callback(callback, state):
    saved_msg = AsyncMock()
    with mock.patch("bot.saved_user_msg", new={callback.from_user.id: saved_msg}):
        await add_callback(callback, state)

        callback.message.answer.assert_called_with(
            text="Введіть дані в наступному форматі:\nслово - значення",
            reply_markup=ADD_IS_DONE_KEYBAORD,
        )
        saved_msg.delete_reply_markup.assert_awaited_once()
        assert await state.get_state() == Form.add_card


@pytest.mark.asyncio
async def test_add_card_state(message, state):
    ...

    await add_card_state(message, state)

    ...
