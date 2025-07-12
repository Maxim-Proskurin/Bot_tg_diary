from aiogram.types import Message
from db.models import Note
from db.session import SessionLocal
from sqlalchemy import select, func
from datetime import datetime, timezone, timedelta
from typing import Any

async def list_handler(msg: Message) -> None:
    
    """ 
    Обрабатывает команду /list.

    Args:
        msg(Message): Список добавленных пользователем заметок.
    """
    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя.")
        return

    page_number = 1
    page_size = 5
    offset = (page_number - 1) * page_size

    async with SessionLocal() as session:
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

async def list_day_handler(msg: Message) -> None:
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
        
async def list_page_handler(msg: Message)-> None:
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