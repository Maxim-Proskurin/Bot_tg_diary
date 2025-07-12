from aiogram.types import Message
from db.models import Note
from db.session import SessionLocal
from sqlalchemy import select
from datetime import datetime, timezone

async def edit_handler(msg: Message)-> None:
    """ 
    Обрабатывает команду /edit.
    
    Args:
        msg(Message): Редактирует заметки по номеру.
    """
    if not msg.text:
        await msg.answer("Пожалуйста, укажи номер заметки для редактирования, например /edit 7")
        return
    parts = msg.text.strip().split()
    if len(parts) < 3 or not parts[1].isdigit():
        await msg.answer("Пожалуйста, укажи номер и новый текст заметки, например: /edit 2 Новый текст")
        return
    note_number = int(parts[1])
    new_text = " ".join(parts[2:])
    if not new_text:
        await msg.answer("Пожалуйста, укажи новый текст заметки после номера.")
        return

    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя.")
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(Note).where(Note.user_id == user_id).order_by(Note.created_at.desc())
        )
        notes = result.scalars().all()
        if not notes or note_number < 1 or note_number > len(notes):
            await msg.answer("Заметка с таким номером не найдена.")
            return
        note_to_edit = notes[note_number - 1]
        setattr(note_to_edit, "text", new_text)
        setattr(note_to_edit, "updated_at", datetime.now(timezone.utc))
        await session.commit()
        await msg.answer(f"Заметка №{note_number} изменена!")
        