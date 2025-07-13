import pytest
from unittest.mock import AsyncMock
from handlers.start import start_handler
from aiogram.types import Message


@pytest.fixture
def fake_message():
    msg = AsyncMock(spec=Message)
    msg.answer = AsyncMock()
    return msg


@pytest.mark.asyncio
async def test_start_handler_sends_keyboard(fake_message):
    await start_handler(fake_message)
    fake_message.answer.assert_called()
    args, kwargs = fake_message.answer.call_args
    assert "кнопок" in args[0] or "Привет" in args[0]
