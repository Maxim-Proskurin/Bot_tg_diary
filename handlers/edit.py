from aiogram.types import Message
from db.models import Note
from db.session import SessionLocal
from sqlalchemy import select
from datetime import datetime, timezone
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class EditNoteState(StatesGroup):
    waiting_for_note_number = State()
    waiting_for_new_text = State()


async def edit_handler(msg: Message, state: FSMContext) -> None:
    """
    Обрабатывает команду /edit.

    Args:
        msg(Message): Редактирует заметки по номеру.
    """
    await msg.answer("Введите номер заметки, которую хотите редактировать!")
    await state.set_state(EditNoteState.waiting_for_note_number)


async def process_edit_note_number(msg: Message, state: FSMContext) -> None:
    """
    Обрабатывает номер заметки для редактирвоания.
    """
    if not msg.text or not msg.text.strip().isdigit():
        await msg.answer("Пожалуйста введите коректный номер заметки!")
        return
    note_number = int(msg.text.strip())
    await state.update_data(note_number=note_number)
    await msg.answer("Введите новый текст для заметки: ")
    await state.set_state(EditNoteState.waiting_for_new_text)


async def proceess_edit_more_text(msg: Message, state: FSMContext) -> None:
    """
    Обрабатывает новый текст заметки и обновляет ее.
    """
    data = await state.get_data()
    note_number = data.get("note_number")
    if not note_number:
        await msg.answer("Ошибка не удалось получить номер заметки.")
        await state.clear()
        return
    if not msg.text:
        await msg.answer("Пожалуйста введите новый текст.")
        return
    new_text = msg.text.strip()
    if not new_text:
        await msg.answer("Текст заметки не может быть пустым.")
        return
    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя.")
        await state.clear()
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(Note)
            .where(Note.user_id == user_id)
            .order_by(Note.created_at.desc())
        )
        notes = result.scalars().all()
        if not notes or note_number < 1 or note_number > len(notes):
            await msg.answer("Заметка с таким номером не найдена.")
            await state.clear()
            return
        note_to_edit = notes[note_number - 1]
        setattr(note_to_edit, "text", new_text)
        setattr(note_to_edit, "updated_at", datetime.now(timezone.utc))
        await session.commit()
        await msg.answer(f"Замтека №{note_number} изменена!")
    await state.clear()
