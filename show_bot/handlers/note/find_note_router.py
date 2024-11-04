from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from create_bot import bot
from data_base.dao import get_all_categories, get_notes_by_user, find_notes_by_category_name
from keyboards.note_kb import generate_category_keyboard, generate_find_category_keyboard, main_note_kb, find_note_kb
from utils_bot.utils import send_many_notes


find_note_router = Router()

class FindNoteStates(StatesGroup):
    text = State()
    category = State()



@find_note_router.message(F.text == "📋 Просмотр заметок")
async def start_views_noti(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Выбери какие заметки отобразить', reply_markup=find_note_kb())  


@find_note_router.message(F.text == "📋 Все заметки")
async def all_views_noti(message: Message, state: FSMContext):
    await state.clear()
    all_notes = await get_notes_by_user(user_id=message.from_user.id)
    if all_notes:
        await send_many_notes(all_notes, bot, message.from_user.id)
        await message.answer(f'Всего {len(all_notes)} заметок', reply_markup=main_note_kb())
    else:
        await message.answer('У вас пока нет ни одной заметки!', reply_markup=main_note_kb())


@find_note_router.message(F.text == "🔍 Поиск по тексту")
async def text_views_noti(message: Message, state: FSMContext):
    await state.clear()
    all_notes = await get_notes_by_user(user_id=message.from_user.id)
    if all_notes:
        await message.answer('Введите поисковой запрос.')
        await state.set_state(FindNoteStates.text)
    else:
        await message.answer('У вас пока нет ни одной заметки!', reply_markup=main_note_kb())


@find_note_router.message(F.text, FindNoteStates.text)
async def text_noti_process(message: Message, state: FSMContext):
    text_search = message.text.strip()
    all_notes = await get_notes_by_user(user_id=message.from_user.id, text_search=text_search)
    await state.clear()
    if all_notes:
        await send_many_notes(all_notes, bot, message.from_user.id)
        await message.answer(f'C поисковой фразой {text_search} было обнаружено {len(all_notes)} заметок!',
                             reply_markup=main_note_kb())
    else:
        await message.answer(f'У вас пока нет ни одной заметки, которая содержала бы в тексте {text_search}!',
                             reply_markup=main_note_kb())
        
        
@find_note_router.message(F.text == "📝 По категории")
async def category_views_noti(message: Message, state: FSMContext):
    await state.clear()
    all_category = await get_all_categories()
    if all_category:
        await message.answer('Выберете категорию',
                             reply_markup=generate_find_category_keyboard(all_category))        
    else:
        await message.answer('У вас пока нет ни одной категории!', reply_markup=main_note_kb())


@find_note_router.callback_query(F.data.startswith('category_name_'))
async def category_noti_process(call: CallbackQuery, state: FSMContext):    
    await state.clear()
    text_name = call.data.replace('category_name_', '')
    print(text_name)
    all_notes = await find_notes_by_category_name(category_name=text_name)
    if all_notes:
        await send_many_notes(all_notes, bot, call.from_user.id)
        await call.message.answer(f'В категории "{text_name}" было обнаружено заметок: {len(all_notes)}',
                             reply_markup=main_note_kb())
    else:
        await call.answer(f'Нет ни одной заметки в категории {text_name}!',
                                reply_markup=main_note_kb())