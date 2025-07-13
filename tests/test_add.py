import pytest
from unittest.mock import AsyncMock, patch
from handlers.add import add_handler, process_note_text, AddNoteStates
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


@pytest.fixture
def fake_message():
    msg = AsyncMock(spec=Message)
    from_user = AsyncMock()
    from_user.id = 123456
    msg.from_user = from_user
    msg.text = "/add"
    msg.answer = AsyncMock()
    return msg


@pytest.fixture
def fake_state():
    return AsyncMock(spec=FSMContext)


@pytest.mark.asyncio
async def test_add_handler_asks_for_text(fake_message, fake_state):
    await add_handler(fake_message, fake_state)
    fake_message.answer.assert_called_with(
        "Введите текст заметки и отправьте его сообщением."
    )
    fake_state.set_state.assert_called_with(
        AddNoteStates.waiting_for_note_text
    )


@pytest.mark.asyncio
@patch("handlers.add.SessionLocal")
async def test_process_note_text_adds_note(
    mock_sessionlocal,
    fake_message,
    fake_state
):
    fake_message.text = "Тестовая заметка"
    session = AsyncMock()
    mock_sessionlocal.return_value.__aenter__.return_value = session
    session.execute.return_value.scalar_one_or_none.return_value = None
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    fake_message.answer = AsyncMock()
    await process_note_text(fake_message, fake_state)
    fake_message.answer.assert_called_with("Заметка добавлена!")
    fake_state.clear.assert_called()
