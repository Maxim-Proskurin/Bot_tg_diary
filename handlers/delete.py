from aiogram.types import Message
from db.models import Note
from db.session import SessionLocal
from sqlalchemy import select


async def delete_handler(msg: Message)-> None:
    """ 
    Обрабатывает команду /delete.
    
    Args:
        msg(Message): Удаление заметок пользователя по номеру.
    """
    if not msg.text:
        await msg.answer("Пожалуйста, укажи номер заметки для удаления, например: /delete 5")
        return
    parts = msg.text.strip().split()
    if len(parts) < 2 or not parts[1].isdigit():
        await msg.answer("Пожалуйста, укажи номер заметки для удаления, например: /delete 5")
        return
    note_number = int(parts[1])

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
        note_to_delete = notes[note_number - 1]
        await session.delete(note_to_delete)
        await session.commit()
        await msg.answer(f"Заметка №{note_number} удалена!")