from aiogram.types import Message
from db.models import Note
from db.session import SessionLocal
from sqlalchemy import select
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class FindNoteStates(StatesGroup):
    waiting_for_query = State()


async def find_handler(msg: Message, state: FSMContext) -> None:
    """
    Обрабатывает команду /find.

    Args:
        msg (Message): Поиск заметок пользователя по ключевому слову.
    """
    await msg.answer("Введите слово или фразу для поиска по заметкам: ")
    await state.set_state(FindNoteStates.waiting_for_query)


async def process_find_query(msg: Message, state: FSMContext) -> None:
    """
    Обрабатывает поискаовый запрос
    пользователя и выводит результат
    """
    if not msg.text or not msg.text.strip():
        await msg.answer("Пожалуйста, введите слово или фразу для поиска.")
        return
    query = msg.text.strip()
    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя.")
        await state.clear()
        return
    async with SessionLocal() as session:
        result = await session.execute(
            select(Note)
            .where(Note.user_id == user_id, Note.text.like(f"%{query}%"))
            .order_by(Note.created_at.desc())
        )
        notes = result.scalars().all()
        if not notes:
            await msg.answer("Ничего не найдено по вашему запросу.")
            await state.clear()
            return
        text = "\n\n".join(
            f"{i+1}. {note.text}\n({note.formatted_time()})"
            for i, note in enumerate(notes)
        )
        await msg.answer(f"Результаты поиска по '{query}':\n\n{text}")
    await state.clear()
