from aiogram.types import Message
from db.models import Note
from db.session import SessionLocal
from sqlalchemy import select
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class DeleteNoteStates(StatesGroup):
    waiting_for_note_number = State()

async def delete_handler(msg: Message, state: FSMContext) -> None:
    """ 
    Обрабатывает команду /delete.
    
    Args:
        msg(Message): Удаление заметок пользователя по номеру.
    """
    await msg.answer("Введите номер заметки для удаления!")
    await state.set_state(DeleteNoteStates.waiting_for_note_number)
async def process_delete_note(msg:Message, state: FSMContext) -> None:
    """ 
    Обрабатывает номер заявки
    """
    if not msg.text or not msg.text.strip().isdigit():
        await msg.answer("Пожалуйста, укажи корректный номер заметки для удаления.")
        return
    
    note_number = int(msg.text.strip())
    user_id = msg.from_user.id if msg.from_user and msg.from_user.id else None
    if not user_id:
        await msg.answer("Ошибочка, не удалось определить пользователя")
        return
    
    async with SessionLocal() as session:
        result = await session.execute(
            select(
                Note).where(
                    Note.user_id == user_id).order_by(
                        Note.created_at.desc()
                        )
            )
        notes = result.scalars().all()
        if not notes or note_number < 1 or note_number > len(notes):
            await msg.answer("Заметка с таким номером не найдена.")
            return
        note_to_delete = notes[note_number - 1]
        await session.delete(note_to_delete)
        await session.commit()
        check_result = await session.execute(
            select(Note).where(Note.id == note_to_delete.id)
        )
        deleted = check_result.scalar_one_or_none()
        if deleted is None:
            await msg.answer(f"Заметка №{note_number} удалена!")
        else:
            await msg.answer("Произошла ошибка при удалении заметки.")
    await state.clear()
 