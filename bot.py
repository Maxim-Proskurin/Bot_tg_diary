import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from heandlers import start_handler, add_handler, list_handler, delete_handler,edit_handler
def get_bot_token() -> str:
    """ 
    Получает токен бота из переменных окружения.
    
    Returnes:
        str: Токен tgbot.
    
    Raises:
        ValueEror: Если токен не найден.
    """
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    if token is None:
        raise ValueError("Токен не найден")
    return token

def setup_dispatcher() -> Dispatcher:
    """ 
    Создает и настраивает диспетчер с хендлерами.
    
    Returns:
        Dispatcher: Настроенный дисптетчер.
    """
    dp = Dispatcher()
    dp.message.register(start_handler, Command("start"))
    dp.message.register(add_handler, Command("add"))
    dp.message.register(list_handler, Command("list"))
    dp.message.register(delete_handler, Command("delete"))
    dp.message.register(edit_handler, Command("edit"))
    return dp

async def run_bot():
    """ 
    Запускает бота.
    """
    bot = Bot(token=get_bot_token())
    dp = setup_dispatcher()
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(run_bot())
    