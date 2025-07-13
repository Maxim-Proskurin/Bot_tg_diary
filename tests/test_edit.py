import pytest
from unittest.mock import AsyncMock, patch, Mock
from handlers.edit import (
    edit_handler,
    process_edit_note_number,
    proceess_edit_more_text,
    EditNoteState,
)
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


@pytest.fixture
def fake_message():
    msg = AsyncMock(spec=Message)
    from_user = AsyncMock()
    from_user.id = 123456
    msg.from_user = from_user
    msg.text = "/edit"
    msg.answer = AsyncMock()
    return msg


@pytest.fixture
def fake_state():
    return AsyncMock(spec=FSMContext)


@pytest.mark.asyncio
async def test_edit_handler_asks_for_number(
    fake_message,
    fake_state
):
    await edit_handler(fake_message, fake_state)
    fake_message.answer.assert_called()
    fake_state.set_state.assert_called_with(
        EditNoteState.waiting_for_note_number
    )


@pytest.mark.asyncio
async def test_process_edit_note_number_asks_for_text(
    fake_message,
    fake_state
):
    fake_message.text = "1"
    await process_edit_note_number(fake_message, fake_state)
    fake_message.answer.assert_called()
    fake_state.set_state.assert_called_with(EditNoteState.waiting_for_new_text)


@pytest.mark.asyncio
@patch("handlers.edit.SessionLocal")
async def test_proceess_edit_more_text_edits_note(
    mock_sessionlocal, fake_message, fake_state
):
    fake_message.text = "new text"
    fake_state.get_data = AsyncMock(return_value={"note_number": 1})
    session = AsyncMock()
    mock_sessionlocal.return_value.__aenter__.return_value = session
    note = Mock()
    note.text = "old text"
    note.formatted_time.return_value = "2024-07-13 12:00"
    scalars_mock = Mock()
    scalars_mock.all.return_value = [note]
    session.execute.return_value.scalars = Mock(return_value=scalars_mock)
    session.commit = AsyncMock()
    fake_message.answer = AsyncMock()
    await proceess_edit_more_text(fake_message, fake_state)
    fake_message.answer.assert_called()
    fake_state.clear.assert_called()
