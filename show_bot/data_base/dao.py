from create_bot import logger
from .base import connection
from .models import User, Note
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from sqlalchemy.exc import SQLAlchemyError


@connection
async def set_user(
    session,
    tg_id: int,
    username: str,
    full_name: str
) -> Optional[User]:
    """Создаем пользователя, если его нет."""
    try:
        user = await session.scalar(select(User).filter_by(id=tg_id))

        if not user:
            new_user = User(id=tg_id, username=username, full_name=full_name)
            session.add(new_user)
            await session.commit()
            logger.info(f"Зарегистрировал пользователя с ID {tg_id}!")
            return None
        else:
            logger.info(f"Пользователь с ID {tg_id} найден!")
            return user
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении пользователя: {e}")
        await session.rollback()


@connection
async def add_note(
    session,
    user_id: int,
    content_type: str,
    caregory: Optional[str] = None,
    content_text: Optional[str] = None,
    file_id: Optional[str] = None
) -> Optional[Note]:
    """Создаем заметку."""
    try:
        user = await session.scalar(select(User).filter_by(id=user_id))
        if not user:
            logger.error(f"Пользователь с ID {user_id} не найден.")
            return None

        new_note = Note(
            user_id=user_id,
            content_type=content_type,
            caregory=caregory,
            content_text=content_text,
            file_id=file_id
        )

        session.add(new_note)
        await session.commit()
        logger.info(
            f"Заметка для пользователя с ID {user_id} успешно добавлена!")
        return new_note
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении заметки: {e}")
        await session.rollback()


@connection
async def update_text_note(
    session,
    note_id: int,
    content_text: str
) -> Optional[Note]:
    """Обновляем текст заметки."""
    try:
        note = await session.scalar(select(Note).filter_by(id=note_id))
        if not note:
            logger.error(f"Заметка с ID {note_id} не найдена.")
            return None

        note.content_text = content_text
        await session.commit()
        logger.info(f"Заметка с ID {note_id} успешно обновлена!")
        return note
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при обновлении заметки: {e}")
        await session.rollback()


@connection
async def update_category_note(
    session,
    note_id: int,
    caregory: str
) -> Optional[Note]:
    """Обновляем категорию заметки."""
    try:
        note = await session.scalar(select(Note).filter_by(id=note_id))
        if not note:
            logger.error(f"Заметка с ID {note_id} не найдена.")
            return None

        note.caregory = caregory
        await session.commit()
        logger.info(f"Заметка с ID {note_id} успешно обновлена!")
        return note
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при обновлении заметки: {e}")
        await session.rollback()
