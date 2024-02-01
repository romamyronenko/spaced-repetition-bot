from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy import create_engine

from bot import (
    Learn,
    Add,
    get_cards,
    cmd_start,
)
from form import Form
from patches import (
    patch_db_manager,
    patch_cmd_start,
    patch_learn_callback,
    patch_redis,
)
from reply_markups import ADD_IS_DONE_KEYBAORD, get_learn_keyboard, START_KEYBOARD
from tests.utils import TEST_USER

engine = create_engine("sqlite://")


@pytest.mark.asyncio
async def test_start_handler(state, message):
    redis_mock = AsyncMock()
    msg = AsyncMock()
    msg.text = "some_text"
    msg.chat.id = 1
    msg.message_id = 1
    message.answer.return_value = msg
    with patch_redis(redis_mock):
        await cmd_start(message, state=state)

    message.answer.assert_called_with(
        text="Привіт, я - бот для запам'ятовування.",
        reply_markup=START_KEYBOARD,
    )
    redis_mock.hset.assert_called_with(
        "saved_messages:start:1",
        mapping={"chat_id": 1, "message_id": 1, "text": "some_text"},
    )


@pytest.mark.asyncio
async def test_get_cards(state, message, db_manager):
    for front, back in (("1", "2"), ("front", "back")):
        db_manager.add_card(front, back, TEST_USER.id)

    with patch_db_manager(db_manager):
        await get_cards(message, state)

    message.answer.assert_called_with(
        text="1 - 2\nfront - back",
    )


@pytest.mark.asyncio
async def test_get_cards_when_empty(state, message, db_manager):
    with patch_db_manager(db_manager):
        await get_cards(message, state)

    message.answer.assert_called_with(
        text="У вас немає карток.",
    )


class TestLearn:
    @pytest.mark.asyncio
    async def test_learn_callback(self, callback, state, db_manager):
        cards = (
            ("front1", "back1"),
            ("front2", "back2"),
            ("front3", "back3"),
            ("front4", "back4"),
        )
        for card in cards:
            db_manager.add_card(*card, callback.from_user.id)

        with patch_db_manager(db_manager), patch_redis(AsyncMock()):
            await Learn.learn_callback(callback, state)

        callback.message.answer.assert_called_with(
            text='front1\n\n<span class="tg-spoiler">back1</span>',
            parse_mode="html",
            reply_markup=get_learn_keyboard(1),
        )

    @pytest.mark.asyncio
    async def test_learn_callback_when_no_cards(self, callback, state, db_manager):
        mock_cmd_start = AsyncMock()
        with patch_cmd_start(mock_cmd_start), patch_db_manager(db_manager), patch_redis(
            AsyncMock()
        ):
            await Learn.learn_callback(callback, state)

        callback.answer.assert_called_with(
            text="На сьогодні ви вже повторили всі слова."
        )

    @pytest.mark.asyncio
    async def test_remember_callback(self, callback, state):
        mock_learn_callback, db_manager = AsyncMock(), AsyncMock()

        callback.data = "remember 1"
        with patch_learn_callback(mock_learn_callback), patch_db_manager(db_manager):
            await Learn.remember_callback(callback, state)

        db_manager.update_remember.assert_called_with("1")
        mock_learn_callback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_forget_callback(self, callback, state):
        mock_forget_callback = AsyncMock()
        db_manager = AsyncMock()
        callback.data = "forget 11"
        with patch_learn_callback(mock_forget_callback), patch_db_manager(db_manager):
            await Learn.forget_callback(callback, state)

        mock_forget_callback.assert_awaited_once()
        db_manager.update_forget.assert_called_with("11")


class TestAdd:
    @pytest.fixture()
    def saved_msg(self):
        retval = AsyncMock()
        yield retval
        retval.reset_mock()

    @pytest.fixture()
    def mock_cmd_start(self):
        retval = AsyncMock()
        yield retval
        retval.reset_mock()

    @pytest.mark.asyncio
    async def test_add_callback(self, callback, state, saved_msg):
        with patch_redis(AsyncMock()) as r:
            r.hgetall.return_value = {"message_id": 1, "chat_id": 1, "text": "sadf"}

            await Add.add_callback(callback, state)

        callback.message.answer.assert_called_with(
            text="Введіть дані в наступному форматі:\nслово - значення",
            reply_markup=ADD_IS_DONE_KEYBAORD,
        )
        callback.bot.edit_message_reply_markup.assert_called_with(1, 1)
        assert await state.get_state() == Form.add_card

    @pytest.mark.asyncio
    async def test_add_card_state(self, message, state):
        db_manager = MagicMock()
        message.text = "front - back"
        with patch_db_manager(db_manager), patch_redis(AsyncMock()) as r:
            r.hgetall.return_value = {
                "message_id": 1,
                "chat_id": 1,
                "text": "some text",
            }
            await Add.add_card_state(message, state)

        message.bot.edit_message_text.assert_called_with(
            text="some text\nfront - back",
            chat_id=1,
            message_id=1,
            reply_markup=ADD_IS_DONE_KEYBAORD,
        )
        message.delete.assert_awaited_once()
        db_manager.add_card.assert_called_with("front", "back", 123)

    @pytest.mark.asyncio
    async def test_add_card_state_wrong_value(self, message, state, db_manager):
        message.text = "wrong"
        with patch_db_manager(db_manager):
            await Add.add_card_state(message, state)

        message.answer.assert_awaited_with("Невірний формат")
        assert await state.get_state() is None

    @pytest.mark.asyncio
    async def test_done_callback(self, callback, state, saved_msg, mock_cmd_start):
        with patch_redis(AsyncMock()) as r, patch_cmd_start(mock_cmd_start):
            r.hgetall.return_value = {
                "message_id": 1,
                "chat_id": 1,
                "text": "some text",
            }

            await Add.done_callback(callback, state)

        callback.bot.edit_message_reply_markup.assert_awaited_once()
        mock_cmd_start.assert_awaited_with(callback.message, state)
        assert await state.get_state() is None
