from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from create_bot import bot
from data_base.dao import add_note, get_all_categories, get_category_by_id
from keyboards.note_kb import main_note_kb, add_note_check, generate_category_keyboard, main_category_kb
from keyboards.other_kb import stop_fsm
from utils_bot.utils import get_content_info, send_message_user


add_note_router = Router()

class AddNoteStates(StatesGroup):
    content = State() 
    check_state = State() 

    
@add_note_router.message(F.text == '📝 Заметки')
async def start_note(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Ты в меню заметок. Выбери необходимое действие.',
                         reply_markup=main_note_kb())    
    

@add_note_router.message(F.text == '📝 Добавить заметку')
async def category_views_noti(message: Message, state: FSMContext):
    await state.clear()
    all_category = await get_all_categories(user_id=message.from_user.id)
    await message.answer('⭐️ Добавьте новую категорию с помощью меню', reply_markup=main_category_kb())    
    if all_category:
        await message.answer('или выберете из представленных:',
                             reply_markup=generate_category_keyboard(all_category))
    else:
        await message.answer('У вас нет ни одной категории. Добавьте ее👇!', reply_markup=main_category_kb())        


@add_note_router.callback_query(F.data.startswith('category_id_'))
async def start_add_note(call: CallbackQuery, state: FSMContext):
    category_id = int(call.data.replace('category_id_', ''))
    await state.update_data(category_id=category_id)
    category = await get_category_by_id(category_id)
    category_name= category['category_name']    
    await call.message.answer(
        f'Добавьте заметку для категории "{category_name}"',
        reply_markup=stop_fsm()
    )
    await state.set_state(AddNoteStates.content)


@add_note_router.message(AddNoteStates.content)
async def handle_user_note_message(message: Message, state: FSMContext):   
    data = await state.get_data()
    cat_id = data.get('category_id')
    category = await get_category_by_id(cat_id)    
    content_info = get_content_info(message)    
    if content_info.get('content_type'):
        await state.update_data(**content_info)

        text = (f"Новая заметка 📚\n\n"                
                f"Категория ⭐️ <u>{category['category_name']}</u>\n"
                "Текст:\n"
                f"<b>{content_info['content_text'] if content_info['content_text'] else 'Отсутствует'}</b>\n\n"                
                f"Все ли верно💡")
        await send_message_user(bot=bot, content_type=content_info['content_type'], content_text=text,
                                user_id=message.from_user.id, file_id=content_info['file_id'],
                                kb=add_note_check())
        await state.set_state(AddNoteStates.check_state)
    else:
        await message.answer(
            'Я не знаю как работать с таким медафайлом. Нужно что-то другое.'
        )
        await state.set_state(AddNoteStates.content)
        

@add_note_router.message(AddNoteStates.check_state, F.text == "✅ Все верно")
async def confirm_add_note(message: Message, state: FSMContext):
    note = await state.get_data()
    cat_id = int(note.get('category_id'))    
    await add_note(user_id=message.from_user.id, caregory_id=cat_id, content_type=note.get('content_type'),
                   content_text=note.get('content_text'), file_id=note.get('file_id'))
    await message.answer('Заметка успешно добавлена!', reply_markup=main_note_kb())
    await state.clear()


@add_note_router.message(AddNoteStates.check_state, F.text == "❌ Отменить")
async def cancel_add_note(message: Message, state: FSMContext):
    await message.answer('Добавление заметки отменено!', reply_markup=main_note_kb())
    await state.clear()    