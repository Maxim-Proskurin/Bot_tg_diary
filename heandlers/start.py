from aiogram.types import Message

async def start_handler(msg: Message):
    """ 
    Обрабатывает команду /start.
    
    Args:
        msg(Message): Входящее сообщение от пользователя.
    """
    await msg.answer("Здорова! Че записывать будем?")