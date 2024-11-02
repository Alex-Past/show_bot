from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from create_bot import bot
from data_base.dao import add_note
from keyboards.note_kb import main_note_kb, add_note_check
from keyboards.other_kb import stop_fsm
from utils_bot.utils import get_content_info, send_message_user


add_note_router = Router()

class AddNoteStates(StatesGroup):
    content = State()  # Ожидаем любое сообщение от пользователя
    check_state = State()  # Финальна проверка

    
@add_note_router.message(F.text == '📝 Заметки')
async def start_note(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Ты в меню добавления заметок. Выбери необходимое действие.',
                         reply_markup=main_note_kb())    
    

@add_note_router.message(F.text == '📝 Добавить заметку')
async def start_add_note(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Отправь сообщение в любом формате (текст, медиа или медиа + текст). '
                         'В случае если к медиа требуется подпись - оставь ее в комментариях к медиа-файлу ',
                         reply_markup=stop_fsm())
    await state.set_state(AddNoteStates.content)    


@add_note_router.message(AddNoteStates.check_state, F.text == '✅ Все верно')
async def confirm_add_note(message: Message, state: FSMContext):
    note = await state.get_data()
    await add_note(user_id=message.from_user.id, content_type=note.get('content_type'),
                   content_text=note.get('content_text'), file_id=note.get('file_id'))
    await message.answer('Заметка успешно добавлена!', reply_markup=main_note_kb())
    await state.clear()


@add_note_router.message(AddNoteStates.check_state, F.text == '❌ Отменить')
async def cancel_add_note(message: Message, state: FSMContext):
    await message.answer('Добавление заметки отменено!', reply_markup=main_note_kb())
    await state.clear()    