from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from data_base.dao import delete_category, update_category
from keyboards.note_kb import main_note_kb


upd_cat_router = Router()

class UPDNoteStates(StatesGroup):
    text = State()


@upd_cat_router.callback_query(F.data.startswith('edit_cat_text_'))
async def edit_cat_text_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    cat_id = int(call.data.replace('edit_cat_text_', ''))
    await call.answer(f'✍️ Режим редактирования категории')
    await state.update_data(cat_id=cat_id)
    await call.message.answer(f'Введи новое название категории 👇')
    await state.set_state(UPDNoteStates.text)


@upd_cat_router.message(F.text, UPDNoteStates.text)
async def confirm_edit_cat_text(message: Message, state: FSMContext):
    cat_data = await state.get_data()
    cat_id = cat_data.get('cat_id')
    text = message.text.strip()
    await update_category(category_id=cat_id, text_name=text)
    await state.clear()
    await message.answer(f'Название категории с ID {cat_id} успешно изменен на "{text}"!',
                         reply_markup=main_note_kb())


@upd_cat_router.callback_query(F.data.startswith('dell_cat_'))
async def dell_cat_process(call: CallbackQuery, state: FSMContext):
    await state.clear()
    cat_id = int(call.data.replace('dell_cat_', ''))
    await delete_category(category_id=cat_id)
    await call.answer(f'Категория удалена!', show_alert=True)
    await call.message.delete()