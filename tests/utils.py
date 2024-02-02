"""
Objects for tests
"""

from aiogram.types import User, Chat

TEST_USER = User(
    id=123, is_bot=False, first_name="Test", last_name="Bot", username="testbot"
)

TEST_USER_CHAT = Chat(
    id=12,
    type="private",
    username=TEST_USER.username,
    first_name=TEST_USER.first_name,
    last_name=TEST_USER.last_name,
)
