from aiogram.types import Message
from aiogram.filters import Command
from db.models import Note, User
from db.session import SessionLocal
from sqlalchemy import select

async def start_handler(msg: Message):
    """ 
    Обрабатывает команду /start.
    
    Args:
        msg(Message): Входящее сообщение от пользователя.
    """
    await msg.answer("Здорова! Че записывать будем?")

async def add_handler(msg: Message):
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
        note = Note(user_id=user_id, text=note_text)
        session.add(note)
        await session.commit()
    await msg.answer("Зафиксировали")
    
    
async def list_handler(msg: Message):
    """ 
    Обрабатывает команду /list.
    
    Args:
        msg(Message): Список добавленных пользователем заметок.
    """
    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя.")
        return
    async with SessionLocal() as session:
        result = await session.execute(
            select(Note).where(Note.user_id == user_id).order_by(Note.created_at.desc())
        )
        notes = result.scalars().all()
        if notes:
            text = "\n\n".join(
                f"{i+1}. {note.text}\n({note.formatted_time()})"
                for i, note in enumerate(notes)
            )
            await msg.answer(f"Твои записи:\n\n{text}")
        
    
    