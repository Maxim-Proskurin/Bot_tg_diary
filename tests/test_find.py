import pytest
from unittest.mock import AsyncMock, patch, Mock
from handlers.find import (
    find_handler,
    process_find_query,
    FindNoteStates
)
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


@pytest.fixture
def fake_message():
    msg = AsyncMock(spec=Message)
    from_user = AsyncMock()
    from_user.id = 123456
    msg.from_user = from_user
    msg.text = "/find"
    msg.answer = AsyncMock()
    return msg


@pytest.fixture
def fake_state():
    return AsyncMock(spec=FSMContext)


@pytest.mark.asyncio
async def test_find_handler_asks_for_query(fake_message, fake_state):
    await find_handler(fake_message, fake_state)
    fake_message.answer.assert_called()
    fake_state.set_state.assert_called_with(FindNoteStates.waiting_for_query)


@pytest.mark.asyncio
@patch("handlers.find.SessionLocal")
async def test_process_find_query_found(
    mock_sessionlocal,
    fake_message,
    fake_state
):
    fake_message.text = "test"
    session = AsyncMock()
    mock_sessionlocal.return_value.__aenter__.return_value = session
    note = Mock()
    note.text = "Test"
    note.formatted_time.return_value = "2024-07-13 12:00"
    scalars_mock = Mock()
    scalars_mock.all.return_value = [note]

    session.execute.return_value.scalars = Mock(return_value=scalars_mock)
    session.commit = AsyncMock()
    fake_message.answer = AsyncMock()
    await process_find_query(fake_message, fake_state)
    fake_message.answer.assert_called()
    fake_state.clear.assert_called()
