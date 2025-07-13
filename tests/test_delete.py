import pytest
from unittest.mock import AsyncMock, patch
from unittest.mock import Mock
from handlers.delete import (
    delete_handler,
    process_delete_note,
    DeleteNoteStates
)
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from db.models import Note


@pytest.fixture
def fake_message():
    msg = AsyncMock(spec=Message)
    from_user = AsyncMock()
    from_user.id = 123456
    msg.from_user = from_user
    msg.text = "/delete"
    msg.answer = AsyncMock()
    return msg


@pytest.fixture
def fake_state():
    return AsyncMock(spec=FSMContext)


@pytest.mark.asyncio
async def test_delete_handler_asks_for_number(
    fake_message,
    fake_state
):
    await delete_handler(fake_message, fake_state)
    fake_message.answer.assert_called_with(
        "Введите номер заметки для удаления!"
        )
    fake_state.set_state.assert_called_with(
        DeleteNoteStates.waiting_for_note_number
        )


@pytest.mark.asyncio
@patch("handlers.delete.SessionLocal")
async def test_process_delete_note_deletes_note(
    mock_sessionlocal, fake_message, fake_state
):
    fake_message.text = "1"
    session = AsyncMock()
    mock_sessionlocal.return_value.__aenter__.return_value = session

    note = AsyncMock(spec=Note)
    scalars_mock = Mock()
    scalars_mock.all.return_value = [note]

    session.execute.side_effect = [
        Mock(scalars=Mock(return_value=scalars_mock)),
        Mock(scalar_one_or_none=Mock(return_value=None)),
    ]

    session.delete = AsyncMock()
    session.commit = AsyncMock()
    fake_message.answer = AsyncMock()

    await process_delete_note(fake_message, fake_state)
    fake_message.answer.assert_any_call("Заметка №1 удалена!")
    fake_state.clear.assert_called()


@pytest.mark.asyncio
@patch("handlers.delete.SessionLocal")
async def test_process_delete_note_invalid_number(fake_message, fake_state):
    fake_message.text = "abc"
    fake_message.answer = AsyncMock()
    await process_delete_note(fake_message, fake_state)
    print([call.args for call in fake_message.answer.call_args_list])
    assert any(
        "корректный номер" in str(call.args[0])
        for call in fake_message.answer.call_args_list
    )


@pytest.mark.asyncio
@patch("handlers.delete.SessionLocal")
async def test_process_delete_note_no_notes(
    mock_sessionlocal, fake_message, fake_state
):
    fake_message.text = "1"
    session = AsyncMock()
    mock_sessionlocal.return_value.__aenter__.return_value = session

    scalars_mock = Mock()
    scalars_mock.all.return_value = []
    session.execute.side_effect = [
        Mock(scalars=Mock(return_value=scalars_mock)),
    ]

    fake_message.answer = AsyncMock()
    await process_delete_note(fake_message, fake_state)
    fake_message.answer.assert_any_call("Заметка с таким номером не найдена.")


@pytest.mark.asyncio
@patch("handlers.delete.SessionLocal")
async def test_process_delete_note_user_not_found(
    mock_sessionlocal, fake_message, fake_state
):
    fake_message.text = "1"
    fake_message.from_user = None
    await process_delete_note(fake_message, fake_state)
    fake_message.answer.assert_called_with(
        "Ошибочка, не удалось определить пользователя"
    )
