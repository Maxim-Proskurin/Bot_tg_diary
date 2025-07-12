from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.models import Note, User
from db.session import SessionLocal
from sqlalchemy import select
from datetime import datetime, timezone

class AddNoteStates(StatesGroup):
    waiting_for_note_text = State()

async def add_handler(msg: Message, state: FSMContext) -> None:
    """
    Обрабатывает нажатие на кнопку "➕ Добавить заметку" или команду /add.
    Переводит пользователя в состояние ожидания ввода текста заметки.
    """
    await msg.answer("Введите текст заметки и отправьте его сообщением.")
    await state.set_state(AddNoteStates.waiting_for_note_text)

async def process_note_text(msg: Message, state: FSMContext) -> None:
    """
    Обрабатывает текст заметки, введённый пользователем.
    """
    note_text = msg.text.strip()
    if not note_text:
        await msg.answer("Текст заметки не может быть пустым. Попробуйте ещё раз.")
        return
    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя.")
        return
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            user = User(id=user_id)
            session.add(user)
            await session.flush()
        now = datetime.now(timezone.utc)
        note = Note(user_id=user_id, text=note_text, updated_at=now)
        session.add(note)
        await session.commit()
    await msg.answer("Заметка добавлена!")
    await state.clear()