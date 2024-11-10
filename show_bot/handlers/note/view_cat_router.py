from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from create_bot import bot
from data_base.dao import get_all_categories, get_notes_by_user
from keyboards.note_kb import main_note_kb, find_note_kb
from utils_bot.utils import send_many_categories, send_many_notes


view_cat_router = Router()


@view_cat_router.message(F.text == "📋 Все категории")
async def all_views_category(message: Message, state: FSMContext):    
    all_category = await get_all_categories()
    if all_category:
        await message.answer(f'⭐️ Найдено всего {len(all_category)} категорий', reply_markup=main_note_kb())
        await send_many_categories(all_category, bot, message.from_user.id)
    else:
        await message.answer('У вас пока нет ни одной категории!', reply_markup=main_note_kb())    