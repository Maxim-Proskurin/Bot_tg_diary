from aiogram.types import Message
from aiogram.filters import Command


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
    await msg.answer("Добавим запись?")
    
async def list_handler(msg: Message):
    """ 
    Обрабатывает команду /list.
    
    Args:
        msg(Message): Список добавленных пользователем заметок.
    """
    await msg.answer("Твои записи.")
    
    