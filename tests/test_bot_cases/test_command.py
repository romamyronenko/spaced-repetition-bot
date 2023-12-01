from unittest.mock import AsyncMock

import pytest

from bot import cmd_start_help, dp


@pytest.mark.asyncio
async def test_start():
    message = AsyncMock()
    await cmd_start_help(message, AsyncMock())

    message.answer.assert_called_once_with(text='Hello😃')

