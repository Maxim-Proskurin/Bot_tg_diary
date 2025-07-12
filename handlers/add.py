from aiogram.types import Message
from db.models import Note, User
from db.session import SessionLocal
from sqlalchemy import select
from datetime import datetime, timezone

async def add_handler(msg: Message)-> None:
    """ 
    Обрабатывает команду /add.
    
    Args:
        msg(Message): Добавление заметки от пользователя.
    """
    if not msg.text:
        await msg.answer("Ошибочка, не удалось получить текст!")
        return
    note_text = msg.text.removeprefix('/add').strip()
    if not note_text:
        await msg.answer("Напиши текст заметки после /add.")
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
    await msg.answer("Зафиксировали")