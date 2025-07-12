from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

async def start_handler(msg: Message) -> None:
    """ 
    Обрабатывает команду /start.

    Args:
        msg(Message): Входящее сообщение от пользователя.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить заметку"), KeyboardButton(text="📋 Список заметок")],
            [KeyboardButton(text="❌ Удалить заметку"), KeyboardButton(text="✏️ Изменить заметку")],
            [KeyboardButton(text="📅 Заметки за N дней"), KeyboardButton(text="📄 Заметки по страницам")],
            [KeyboardButton(text="🔍 Поиск по заметкам")]
        ],
        resize_keyboard=True
    )
    await msg.answer(
        "👋 Привет! Я твой ежедневник.\n\n"
        "Выбери действие с помощью кнопок или команд:\n"
        "➕ Добавить заметку - добавить новую запись\n"
        "📋 Список заметок - посмотреть свои заметки\n"
        "❌ Удалить заметку - удалить запись по номеру\n"
        "✏️ Изменить заметку - изменить текст записи\n"
        "📅 Заметки за N дней - фильтр по времени\n"
        "📄 Заметки по страницам - листать по страницам\n"
        "🔍 Поиск по заметкам - найти запись по слову",
        reply_markup=keyboard
    )