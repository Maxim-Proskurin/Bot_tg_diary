from aiogram.types import Message
from aiogram.filters import Command
from db.models import Note
from db.session import SessionLocal


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
    await msg.answer("Твои записи.")
    
    