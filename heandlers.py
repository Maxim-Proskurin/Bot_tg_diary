from aiogram.types import Message
from db.models import Note, User
from db.session import SessionLocal
from sqlalchemy import select, func
from datetime import datetime, timezone, timedelta

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
        now = datetime.now(timezone.utc)
        note = Note(user_id=user_id, text=note_text, updated_at=now)
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

    # Пагинация по умолчанию: первая страница, 5 заметок
    page_number = 1
    page_size = 5
    offset = (page_number - 1) * page_size

    async with SessionLocal() as session:
        # Считаем общее количество заметок пользователя
        count_result = await session.execute(
            select(func.count()).where(Note.user_id == user_id)
        )
        total_notes = count_result.scalar_one()
        total_pages = (total_notes + page_size - 1) // page_size

        result = await session.execute(
            select(Note)
            .where(Note.user_id == user_id)
            .order_by(Note.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        notes = result.scalars().all()
        if not notes:
            await msg.answer("У тебя пока нет записей.")
            return
        text = "\n\n".join(
            f"{offset + i + 1}. {note.text}\n({note.formatted_time()})"
            for i, note in enumerate(notes)
        )
        await msg.answer(f"Страница 1 из {total_pages}:\n\n{text}")
        
async def delete_handler(msg: Message):
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

async def edit_handler(msg: Message):
    """ 
    Обрабатывает команду /edit.
    
    Args:
        msg(Message): Редактирует заметки по номеру.
    """
    if not msg.text:
        await msg.answer("Пожалуйста, укажи номер заметки для редактирования, например /edit 7")
        return
    parts = msg.text.strip().split()
    if len(parts) < 3 or not parts[1].isdigit():
        await msg.answer("Пожалуйста, укажи номер и новый текст заметки, например: /edit 2 Новый текст")
        return
    note_number = int(parts[1])
    new_text = " ".join(parts[2:])
    if not new_text:
        await msg.answer("Пожалуйста, укажи новый текст заметки после номера.")
        return

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
        note_to_edit = notes[note_number - 1]
        setattr(note_to_edit, "text", new_text)
        setattr(note_to_edit, "updated_at", datetime.now(timezone.utc))
        await session.commit()
        await msg.answer(f"Заметка №{note_number} изменена!")
        

async def list_day_handler(msg: Message):
    """ 
    Обрабатывает команду /list_days.

    Args:
        msg(Message): выводит заметки за N дней.
    """
    if not msg.text:
        await msg.answer("Пожалуйста, укажи за сколько дней показать заметки, например: /list_days 3")
        return
    parts = msg.text.strip().split()
    if len(parts) < 2 or not parts[1].isdigit():
        await msg.answer("Пожалуйста, укажи за сколько дней показать заметки, например: /list_days 3")
        return
    day_number = int(parts[1])
    if day_number < 1:
        await msg.answer("Число дней должно быть больше нуля.")
        return
    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя.")
        return

    
    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=day_number)

    async with SessionLocal() as session:
        result = await session.execute(
            select(Note)
            .where(
                Note.user_id == user_id,
                Note.created_at >= date_from
            )
            .order_by(Note.created_at.desc())
        )
        notes = result.scalars().all()
        if not notes:
            await msg.answer("Заметок за этот период не найдено!")
            return
        text = "\n\n".join(
            f"{i+1}. {note.text}\n({note.formatted_time()})"
            for i, note in enumerate(notes)
        )
        await msg.answer(f"Твои записи за последние {day_number} дней:\n\n{text}")
        
async def list_page_handler(msg: Message):
    """ 
    Обрабатывает команду /list_page.
    
    Args:
        msg(Message): Выводит определенное количество заметок на страницу.
    """
    if not msg.text:
        await msg.answer("Пожалуйста укажите страницу для вывода! например /list_page 6")
        return
    page = msg.text.strip().split()
    if len(page) < 2 or not page[1].isdigit():
        await msg.answer("Пожалуйста, укажи номер страницы для вывода, например: /list_page 2")
        return
    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя.")
        return
    
    page_number = int(page[1])
    page_size = 5
    offset = (page_number - 1) * page_size

    async with SessionLocal() as session:
        # Считаем общее количество заметок пользователя
        count_result = await session.execute(
            select(func.count()).where(Note.user_id == user_id)
        )
        total_notes = count_result.scalar_one()
        total_pages = (total_notes + page_size - 1) // page_size

        if page_number < 1 or page_number > max(total_pages, 1):
            await msg.answer(f"Такой страницы нет. Всего страниц: {total_pages}")
            return

        result = await session.execute(
            select(Note)
            .where(Note.user_id == user_id)
            .order_by(Note.created_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        notes = result.scalars().all()
        if not notes:
            await msg.answer("На этой странице нет заметок.")
            return
        text = "\n\n".join(
            f"{offset + i + 1}. {note.text}\n({note.formatted_time()})"
            for i, note in enumerate(notes)
        )
        await msg.answer(f"Страница {page_number} из {total_pages}:\n\n{text}")