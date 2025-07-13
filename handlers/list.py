from aiogram.types import Message
from db.models import Note
from db.session import SessionLocal
from sqlalchemy import select, func
from datetime import datetime, timezone, timedelta
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class ListDaysStaties(StatesGroup):
    waiting_for_days = State()


class ListPageStates(StatesGroup):
    waiting_for_page = State()


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
        await msg.answer(
            (
                f"Страница 1 из {total_pages}:\n\n{text}\n\n"
                "Для следующей страницы используй /list_page 2 "
                "или кнопку 📄 Заметки по страницам."
            )
        )


async def list_day_handler(msg: Message, state: FSMContext) -> None:
    """
    Обрабатывает команду /list_day или кнопку "Заметки за N дней.
    Запрашивает у пользователя количество дней.
    """
    await msg.answer("Введите за сколько дней показать заметки.")
    await state.set_state(ListDaysStaties.waiting_for_days)


async def process_list_days(msg: Message, state: FSMContext) -> None:
    """
    Обрабатывает количество дней,введеное
    пользователем, и выводит заметки
    """
    if not msg.text or not msg.text.strip().isdigit():
        await msg.answer("Пожалуйста, введите коректное число дней.")
        return
    day_number = int(msg.text.strip())
    if day_number < 1:
        await msg.answer("Число дней должно быть больше нуля.")
        return
    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя.")
        await state.clear()
        return

    now = datetime.now(timezone.utc)
    date_from = now - timedelta(days=day_number)

    async with SessionLocal() as session:
        result = await session.execute(
            select(Note)
            .where(Note.user_id == user_id, Note.created_at >= date_from)
            .order_by(Note.created_at.desc())
        )
        notes = result.scalars().all()
        if not notes:
            await msg.answer("Заметок за этот период не найдено.")
            await state.clear()
            return
        text = "\n\n".join(
            f"{i+1}. {note.text}\n({note.formatted_time()})"
            for i,
            note in enumerate(notes)
        )
        await msg.answer(
            f"Твои записи за последние {day_number} дней:\n\n{text}\n\n"
            "Для вывода всех заметок используй /list"
            "или кнопку 📋 Список заметок."
        )
    await state.clear()


async def list_page_handler(msg: Message, state: FSMContext) -> None:
    """
    Обрабатывает команду /list_page.
    Запрашивает у пользователя номер страницы.
    """
    await msg.answer("Введите номер страницы для вывода: ")
    await state.set_state(ListPageStates.waiting_for_page)


async def process_list_page(msg: Message, state: FSMContext) -> None:
    """
    Обрабатывает номер страницы, введенный
    пользователем и выводит заметки
    """
    if not msg.text or not msg.text.strip().isdigit():
        await msg.answer("Пожалуйста, введите коректный номер страницы.")
        return
    page_number = int(msg.text.strip())
    page_size = 5
    offset = (page_number - 1) * page_size
    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя.")
        await state.clear()
        return

    async with SessionLocal() as session:
        count_result = await session.execute(
            select(func.count()).where(Note.user_id == user_id)
        )

        total_notes = count_result.scalar_one()
        total_pages = (total_notes + page_size - 1) // page_size

        if page_number < 1 or page_number > max(
            total_pages, 1
        ):
            await msg.answer(
                "Такой страницы нет. Всего страниц: {total_pages}"
                )
            await state.clear()
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
            await msg.answer("На этой странице заметок нет.")
            await state.clear()
            return
        text = "\n\n".join(
            f"{offset + i + 1}. {note.text}\n({note.formatted_time()})"
            for i,
            note in enumerate(notes)
        )
        await msg.answer(
            f"Страница {page_number} из {total_pages}:\n\n{text}\n\n"
            "Для другой страницы используй /list_page N"
            "или кнопку 📄 Заметки по страницам."
        )
    await state.clear()
