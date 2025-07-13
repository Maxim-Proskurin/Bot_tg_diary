import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from handlers.add import add_handler, process_note_text, AddNoteStates
from handlers.delete import delete_handler, process_delete_note,DeleteNoteStates
from handlers.edit import edit_handler, process_edit_note_number, EditNoteState
from handlers.start import start_handler
from handlers.list import list_handler, list_day_handler, list_page_handler
from handlers.find import find_handler
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

def setup_dispatcher(dp: Dispatcher) -> None:
    """
    Регистрирует все хендлеры в диспетчере.

    Args:
        dp (Dispatcher): Диспетчер aiogram.
    """
    dp.message.register(start_handler, Command("start"))
    dp.message.register(add_handler, lambda msg, **_: msg.text in ["/add", "➕ Добавить заметку"])
    dp.message.register(process_note_text, AddNoteStates.waiting_for_note_text)
    dp.message.register(list_handler, Command("list"))
    dp.message.register(delete_handler, lambda msg, **_: msg.text in ["/delete", "❌ Удалить заметку"])
    dp.message.register(process_delete_note, DeleteNoteStates.waiting_for_note_number)
    dp.message.register(edit_handler, lambda msg, **_: msg.text in ["/edit", "✏️ Изменить заметку"])
    dp.message.register(process_edit_note_number, EditNoteState.waiting_for_note_number)
    dp.message.register(list_day_handler, Command("list_days"))
    dp.message.register(list_page_handler, Command("list_page"))
    dp.message.register(find_handler, Command("find"))

async def run_bot():
    """ 
    Запускает бота.
    """
    bot = Bot(token=get_bot_token())
    dp = Dispatcher(storage=MemoryStorage())
    setup_dispatcher(dp)
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(run_bot())
    