from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from create_bot import bot
from data_base.dao import get_all_categories, get_notes_by_user, find_notes_by_category_name
from keyboards.note_kb import generate_category_keyboard, generate_find_category_keyboard, main_note_kb, find_note_kb
from utils_bot.utils import send_many_notes


find_cat_router = Router()

class FindNoteStates(StatesGroup):
    cat_text = State()    
    category = State()


        
        
@find_cat_router.message(F.text == "📝 Все категории")
async def category_views_noti(message: Message, state: FSMContext):
    await state.clear()
    all_category = await get_all_categories()
    if all_category:
        await message.answer('Выберете категорию',
                             reply_markup=generate_find_category_keyboard(all_category))        
    else:
        await message.answer('У вас пока нет ни одной категории!', reply_markup=main_note_kb())


@find_cat_router.callback_query(F.data.startswith('category_name_'))
async def category_noti_process(call: CallbackQuery, state: FSMContext):    
    await state.clear()
    text_name = call.data.replace('category_name_', '')    
    all_notes = await find_notes_by_category_name(category_name=text_name)
    if all_notes:
        await call.message.answer(f'В категории "{text_name}" заметок: {len(all_notes)}',
                             reply_markup=main_note_kb())
        await send_many_notes(all_notes, bot, call.from_user.id)
    else:
        await call.answer(f'Нет ни одной заметки в категории {text_name}!',
                                reply_markup=main_note_kb())    
        

@find_cat_router.message(F.text == "🔍 Поиск категории")
async def text_category_noti(message: Message, state: FSMContext):
    await state.clear()
    all_notes = await get_notes_by_user(user_id=message.from_user.id)
    if all_notes:
        await message.answer('Введите поисковой запрос.')
        await state.set_state(FindNoteStates.cat_text)
    else:
        await message.answer('У вас пока нет ни одной заметки!', reply_markup=main_note_kb())


@find_cat_router.message(F.text, FindNoteStates.cat_text)
async def text_category_process(message: Message, state: FSMContext):    
    text_search = message.text.strip()
    tar_category = await get_all_categories(text_search=text_search)
    await state.clear()
    if tar_category:
        await message.answer('Найдены категории:',
                             reply_markup=generate_find_category_keyboard(tar_category))        
    else:
        await message.answer(f'Не найдено ни одной категории с именем "{text_search}"!', reply_markup=main_note_kb())