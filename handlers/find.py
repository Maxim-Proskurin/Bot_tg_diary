from aiogram.types import Message
from db.models import Note
from db.session import SessionLocal
from sqlalchemy import select
from typing import Optional

async def find_handler(msg: Message) -> None:
    """
    Обрабатывает команду /find.

    Args:
        msg (Message): Поиск заметок пользователя по ключевому слову.
    """
    if not msg.text:
        await msg.answer("Пожалуйста, укажи слово для поиска, например: /find важное")
        return
    parts = msg.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        await msg.answer("Пожалуйста, укажи слово для поиска, например: /find важное")
        return
    query = parts[1].strip()
    if not query:
        await msg.answer("Пожалуйста, укажи слово для поиска, например: /find важное")
        return

    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя.")
        return

    async with SessionLocal() as session:
        result = await session.execute(
            select(Note)
            .where(
                Note.user_id == user_id,
                Note.text.ilike(f"%{query}%")
            )
            .order_by(Note.created_at.desc())
        )
        notes = result.scalars().all()
        if not notes:
            await msg.answer("Ничего не найдено по вашему запросу.")
            return
        text = "\n\n".join(
            f"{i+1}. {note.text}\n({note.formatted_time()})"
            for i, note in enumerate(notes)
        )
        await msg.answer(f"Результаты поиска по '{query}':\n\n{text}")