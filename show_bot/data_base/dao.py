from create_bot import logger
from .base import connection
from .models import Category, User, Note
from sqlalchemy import select
from sqlalchemy.orm import selectinload
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
async def add_category(
    session,
    text_name: str,
) -> Optional[Category]:
    """Создаем категорию, если ее нет."""
    try:
        category = await session.scalar(select(Category).filter_by(name=text_name))

        if not category:
            new_category = Category(name=text_name)
            session.add(new_category)
            await session.commit()
            logger.info(f"Добавлена новая категория: {text_name}!")
            return new_category
        else:
            logger.info(f"Категория {text_name} уже существует!")
            return None
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении категории: {e}")
        await session.rollback()


@connection
async def update_category(
    session,
    category_id: int,
    text_name: str
) -> Optional[Note]:
    """Обновляем название категории."""
    try:
        category = await session.scalar(select(Category).filter_by(id=category_id))
        if not category:
            logger.error(f"Категория '{text_name}' не найдена.")
            return None

        category.name = text_name
        await session.commit()
        logger.info(f"Категория '{text_name}' успешно обновлена!")
        return category
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при обновлении категории: {e}")
        await session.rollback()


@connection
async def add_note(
    session,
    user_id: int,
    content_type: str,
    caregory_id: int,
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
            category_id=caregory_id,
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
async def get_note_by_id(session, note_id: int) -> Optional[Dict[str, Any]]:
    try:
        stmt = select(Note).options(
            selectinload(Note.category)
        ).where(Note.id == note_id)
        result = await session.execute(stmt)
        note = result.scalar_one_or_none()
        if not note:
            logger.info(f"Заметка с ID {note_id} не найдена.")
            return None

        return {
            'id': note.id,
            'category_name': note.category.name if note.category else "Без категории",
            'content_type': note.content_type,
            'content_text': note.content_text,
            'file_id': note.file_id
        }
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении заметки: {e}")
        return None


@connection
async def get_category_by_id(session, cat_id: int) -> Optional[Dict[str, Any]]:
    try:
        stmt = select(Category).where(Category.id == cat_id)
        category = await session.scalar(stmt)        
        if not category:
            logger.info(f"Категория с ID {cat_id} не найдена.")
            return None

        return {
            'id': category.id,
            'category_name': category.name
        }
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении категории: {e}")
        return None



@connection
async def delete_note_by_id(session, note_id: int) -> Optional[Note]:
    try:
        note = await session.get(Note, note_id)
        if not note:
            logger.error(f"Заметка с ID {note_id} не найдена.")
            return None

        await session.delete(note)
        await session.commit()
        logger.info(f"Заметка с ID {note_id} успешно удалена.")
        return note
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при удалении заметки: {e}")
        await session.rollback()
        return None


@connection
async def get_all_categories(session) -> List[Dict[str, Any]]:
    try:        
        stmt = select(Category)
        result = await session.execute(stmt)
        categories = result.scalars().all()
        if not categories:
            logger.info("Категории не найдены.")
            return []
        
        cat_list = [
            {
                'id': cat.id,
                'category_name': cat.name                
            } for cat in categories
        ]
        return cat_list

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении категорий: {e}")
        return []

        
    


@connection
async def get_notes_by_user(
    session,
    user_id: int,
    text_search: Optional[str] = None,
    category_id: Optional[int] = None
) -> List[Dict[str, Any]]:
    try:
        stmt = select(Note).filter(Note.user_id == user_id)

        if category_id is not None:
            stmt = stmt.filter(Note.category_id == category_id)

        result = await session.execute(stmt)
        notes = result.scalars().all()

        if not notes:
            logger.info("Заметки для пользователя"
                        f" с ID {user_id} не найдены.")
            return []

        note_list = [
            {
                'id': note.id,
                'content_type': note.content_type,
                'content_text': note.content_text,
                'file_id': note.file_id,
                'date_created': note.created_at
            } for note in notes
        ]

        if text_search:
            note_list = [
                note for note in note_list
                if text_search.lower() in (note['content_text'] or '').lower()
            ]

        return note_list

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при получении заметок: {e}")
        return []
