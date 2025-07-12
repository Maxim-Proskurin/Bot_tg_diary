from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

async def start_handler(msg: Message) -> None:
    """ 
    Обрабатывает команду /start.

    Args:
        msg(Message): Входящее сообщение от пользователя.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/add"), KeyboardButton(text="/list")],
            [KeyboardButton(text="/delete"), KeyboardButton(text="/edit")],
            [KeyboardButton(text="/list_days"), KeyboardButton(text="/list_page")],
            [KeyboardButton(text="/find")]
        ],
        resize_keyboard=True
    )
    await msg.answer(
        "Здорова! Че записывать будем?\n\n"
        "Доступные команды:\n"
        "/add - добавить заметку\n"
        "/list - список заметок\n"
        "/delete - удалить заметку\n"
        "/edit - изменить заметку\n"
        "/list_days - заметки за N дней\n"
        "/list_page - заметки по страницам\n"
        "/find - поиск по заметкам",
        reply_markup=keyboard
    )