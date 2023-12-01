from unittest.mock import AsyncMock

import pytest

from bot import cmd_start_help


@pytest.mark.asyncio
async def test_start_handler():
    message = AsyncMock()
    await cmd_start_help(message, state=None)

    message.answer.assert_called_with(text='Hello😃')


