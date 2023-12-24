import asyncio
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db import Base, DBManager
from tests.mocked_bot import MockedBot
from utils import TEST_USER, TEST_USER_CHAT

engine = create_engine("sqlite://")
session = Session(engine)


@pytest_asyncio.fixture()
async def storage():
    tmp_storage = MemoryStorage()
    try:
        yield tmp_storage
    finally:
        await tmp_storage.close()


@pytest.fixture()
def bot():
    return MockedBot()


@pytest_asyncio.fixture()
async def dispatcher():
    dp = Dispatcher()
    await dp.emit_startup()
    try:
        yield dp
    finally:
        await dp.emit_shutdown()


@pytest.fixture()
def db_manager():
    Base.metadata.create_all(engine)

    yield DBManager(engine)

    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def message():
    message = AsyncMock()
    message.from_user.id = TEST_USER.id
    return message


@pytest.fixture()
def callback():
    callback = AsyncMock()
    callback.from_user.id = TEST_USER.id
    return callback

@pytest.fixture()
def state(storage, bot):
    return FSMContext(
        storage=storage,
        key=StorageKey(bot_id=bot.id, user_id=TEST_USER.id, chat_id=TEST_USER_CHAT.id),
    )
