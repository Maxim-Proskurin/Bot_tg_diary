import pytest
from unittest.mock import AsyncMock, patch, Mock
from handlers.list import (
    list_handler,
    list_day_handler,
    process_list_days,
    list_page_handler,
    process_list_page,
    ListDaysStaties,
    ListPageStates,
)
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


@pytest.fixture
def fake_message():
    msg = AsyncMock(spec=Message)
    from_user = AsyncMock()
    from_user.id = 123456
    msg.from_user = from_user
    msg.text = "/list"
    msg.answer = AsyncMock()
    return msg


@pytest.fixture
def fake_state():
    return AsyncMock(spec=FSMContext)


@pytest.mark.asyncio
@patch("handlers.list.SessionLocal")
async def test_list_handler_shows_notes(mock_sessionlocal, fake_message):
    session = AsyncMock()
    mock_sessionlocal.return_value.__aenter__.return_value = session
    note = Mock()
    note.text = "Test"
    note.formatted_time.return_value = "2024-07-13 12:00"
    session.execute.side_effect = [
        Mock(scalar_one=Mock(return_value=1)),
        Mock(scalars=Mock(return_value=Mock(all=Mock(return_value=[note])))),
    ]
    await list_handler(fake_message)
    fake_message.answer.assert_called()


@pytest.mark.asyncio
async def test_list_day_handler_asks_for_days(fake_message, fake_state):
    await list_day_handler(fake_message, fake_state)
    fake_message.answer.assert_called()
    fake_state.set_state.assert_called_with(ListDaysStaties.waiting_for_days)


@pytest.mark.asyncio
@patch("handlers.list.SessionLocal")
async def test_process_list_days_shows_notes(
    mock_sessionlocal, fake_message, fake_state
):
    fake_message.text = "3"
    session = AsyncMock()
    mock_sessionlocal.return_value.__aenter__.return_value = session
    note = Mock()
    note.text = "Test"
    note.formatted_time.return_value = "2024-07-13 12:00"
    scalars_mock = Mock()
    scalars_mock.all.return_value = [note]
    session.execute.return_value.scalars = Mock(return_value=scalars_mock)
    fake_message.answer = AsyncMock()
    await process_list_days(fake_message, fake_state)
    fake_message.answer.assert_called()
    fake_state.clear.assert_called()


@pytest.mark.asyncio
async def test_list_page_handler_asks_for_page(fake_message, fake_state):
    await list_page_handler(fake_message, fake_state)
    fake_message.answer.assert_called()
    fake_state.set_state.assert_called_with(ListPageStates.waiting_for_page)


@pytest.mark.asyncio
@patch("handlers.list.SessionLocal")
async def test_process_list_page_shows_notes(
    mock_sessionlocal, fake_message, fake_state
):
    fake_message.text = "1"
    session = AsyncMock()
    mock_sessionlocal.return_value.__aenter__.return_value = session
    note = Mock()
    note.text = "Test"
    note.formatted_time.return_value = "2024-07-13 12:00"
    scalars_mock = Mock()
    scalars_mock.all.return_value = [note]
    session.execute.side_effect = [
        Mock(scalar_one=Mock(return_value=1)),
        Mock(scalars=Mock(return_value=scalars_mock)),
    ]
    fake_message.answer = AsyncMock()
    await process_list_page(fake_message, fake_state)
    fake_message.answer.assert_called()
    fake_state.clear.assert_called()
