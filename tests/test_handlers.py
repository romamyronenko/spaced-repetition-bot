from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine

from bot import (
    cmd_start,
    get_cards,
    add_callback,
    saved_user_msg,
    add_card_state,
    remember_callback,
    forget_callback,
    done_callback,
    learn_callback,
)
from form import Form
from reply_markups import START_KEYBOARD, ADD_IS_DONE_KEYBAORD, get_learn_keyboard
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
    db_manager = MagicMock()
    message.text = "front - back"
    saved_msg = AsyncMock()
    saved_msg.text = "some text"
    with mock.patch(
            "bot.saved_user_msg", new={message.from_user.id: saved_msg}
    ), mock.patch("bot.db_manager", new=db_manager):
        await add_card_state(message, state)

    saved_msg.edit_text.assert_called_with(
        text="some text\nfront - back", reply_markup=ADD_IS_DONE_KEYBAORD
    )
    message.delete.assert_awaited_once()
    db_manager.add_card.assert_called_with("front", "back", 123)


@pytest.mark.asyncio
async def test_add_card_state_wrong_value(message, state):
    db_manager = MagicMock()
    message.text = "wrong"
    with mock.patch("bot.db_manager", new=db_manager):
        await add_card_state(message, state)

    message.answer.assert_awaited_with("Невірний формат")
    assert await state.get_state() is None


@pytest.mark.asyncio
async def test_remember_callback(callback, state):
    mock_learn_callback = AsyncMock()
    db_manager = AsyncMock()
    callback.data = "remember 1"
    with mock.patch("bot.learn_callback", new=mock_learn_callback), mock.patch(
            "bot.db_manager", new=db_manager
    ):
        await remember_callback(callback, state)

    db_manager.update_remember.assert_called_with("1")
    mock_learn_callback.assert_awaited_once()


@pytest.mark.asyncio
async def test_done_callback(callback, state):
    saved_msg = AsyncMock()
    mock_cmd_start = AsyncMock()
    callback.message = "msg"
    with mock.patch(
            "bot.saved_user_msg", new={callback.from_user.id: saved_msg}
    ), mock.patch("bot.cmd_start", new=mock_cmd_start):
        await done_callback(callback, state)

    saved_msg.delete_reply_markup.assert_awaited_once()
    mock_cmd_start.assert_awaited_with(callback.message, state)
    assert await state.get_state() is None


@pytest.mark.asyncio
async def test_learn_callback(callback, state, db_manager):
    cards = (
        ("front1", "back1"),
        ("front2", "back2"),
        ("front3", "back3"),
        ("front4", "back4"),
    )
    for card in cards:
        db_manager.add_card(*card, callback.from_user.id)

    with mock.patch("bot.db_manager", new=db_manager):
        await learn_callback(callback, state)

    callback.message.answer.assert_called_with(
        text='front1\n\n<span class="tg-spoiler">back1</span>',
        parse_mode="html",
        reply_markup=get_learn_keyboard(1),
    )


@pytest.mark.asyncio
async def test_learn_callback_when_no_cards(callback, state, db_manager):
    mock_cmd_start = AsyncMock()
    with mock.patch("bot.cmd_start", new=mock_cmd_start), mock.patch("bot.db_manager", new=db_manager):
        await learn_callback(callback, state)

    callback.message.answer.assert_called_with(
        text="На сьогодні ви вже повторили всі слова."
    )
    mock_cmd_start.assert_awaited_once()


@pytest.mark.asyncio
async def test_forget_callback(callback, state):
    callback.data = "forget 11"
    await forget_callback(callback, state)
    callback.message.answer.assert_called_with(text=callback.data)
