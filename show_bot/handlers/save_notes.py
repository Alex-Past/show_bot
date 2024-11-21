import json

from aiogram import Router, F
from aiogram.types import Message, FSInputFile, ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.future import select
from sqlalchemy.orm import subqueryload

from data_base.models import User, Note, Category
from data_base.base import connection

save_router = Router()

class ImportNotesStates(StatesGroup):
    waiting_for_file = State()

@save_router.message(F.text == "/export_notes")
@connection
async def export_notes(session, message: Message, **kwargs):
    """Экспорт заметок в JSON файл."""
    user_id = message.from_user.id
    
    stmt = (
    select(User)
    .where(User.id == user_id)
    .options(
        subqueryload(User.notes),
        subqueryload(User.categories)
        )
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        await message.answer("Вы ещё не создали ни одной заметки.")
        return
    
    data = {
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
        },
        "categories": [
            {"id": c.id, "name": c.name} for c in user.categories
        ],
        "notes": [
            {
                "id": n.id,
                "category_id": n.category_id,
                "content_type": n.content_type,
                "content_text": n.content_text,
                "file_id": n.file_id,
            }
            for n in user.notes
        ],
    }
    
    file_path = f"user_{user_id}_notes.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    file = FSInputFile(file_path)
    await message.answer_document(file)


@save_router.message(F.text == "/import_notes")
async def start_import_notes(message: Message, state: FSMContext):
    """Начинает процесс импорта и ожидает файл."""
    await message.answer("Прикрепите JSON файл с заметками.")
    await state.set_state(ImportNotesStates.waiting_for_file)



@save_router.message(
        F.content_type == ContentType.DOCUMENT,
        ImportNotesStates.waiting_for_file
    )
@connection
async def process_import_notes(
    session, message: Message,
    state: FSMContext, **kwargs
):
    """Обрабатывает прикрепленный файл и выполняет импорт."""
    document = message.document
    if not document.file_name.endswith(".json"):
        await message.answer("Пожалуйста, загрузите файл в формате JSON.")
        return

    file = await message.bot.get_file(document.file_id)
    file_path = file.file_path

    try:        
        file_data = await message.bot.download_file(file_path)
        data = json.loads(file_data.read().decode("utf-8"))
    except json.JSONDecodeError:
        await message.answer(
            "Некорректный формат файла. Загрузите валидный JSON."
        )
        return
    except Exception as e:
        await message.answer(f"Произошла ошибка при обработке файла: {e}")
        return

    user_id = message.from_user.id
    
    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            id=user_id,
            username=data["user"]["username"],
            full_name=data["user"]["full_name"]
        )
        session.add(user)
    
    categories_map = {}
    for category in data.get("categories", []):
        cat = Category(name=category["name"], user=user)
        session.add(cat)
        await session.flush()
        categories_map[category["id"]] = cat.id

    for note in data.get("notes", []):
        session.add(
            Note(
                user=user,
                category_id=categories_map.get(note["category_id"]),
                content_type=note["content_type"],
                content_text=note["content_text"],
                file_id=note["file_id"],
            )
        )

    await session.commit()
    await state.clear()
    await message.answer("Заметки успешно импортированы!")
