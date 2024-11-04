import asyncio
from aiogram.types import Message
from keyboards.note_kb import rule_note_kb

def get_content_info(message: Message):
    content_type = None
    file_id = None

    if message.photo:
        content_type = "photo"
        file_id = message.photo[-1].file_id
    elif message.video:
        content_type = "video"
        file_id = message.video.file_id
    elif message.audio:
        content_type = "audio"
        file_id = message.audio.file_id
    elif message.document:
        content_type = "document"
        file_id = message.document.file_id
    elif message.voice:
        content_type = "voice"
        file_id = message.voice.file_id
    elif message.text:
        content_type = "text"

    content_text = message.text or message.caption
    return {'content_type': content_type, 'file_id': file_id, 'content_text': content_text}


async def send_message_user(bot, user_id, content_type, content_text=None, file_id=None, kb=None):
    match content_type:
        case 'text': await bot.send_message(chat_id=user_id, text=content_text, reply_markup=kb)
        case 'photo': await bot.send_photo(chat_id=user_id, photo=file_id, caption=content_text, reply_markup=kb)
        case 'document': await bot.send_document(chat_id=user_id, document=file_id, caption=content_text, reply_markup=kb)
        case 'video': await bot.send_video(chat_id=user_id, video=file_id, caption=content_text, reply_markup=kb)
        case 'audio': await bot.send_audio(chat_id=user_id, audio=file_id, caption=content_text, reply_markup=kb)
        case 'voice': await bot.send_voice(chat_id=user_id, voice=file_id, caption=content_text, reply_markup=kb)


async def send_many_notes(all_notes, bot, user_id):
    for note in all_notes:
        try:
            text = (f"Заметка:\n\n"                   
                    f"Текст: <b>{note['content_text'] if note['content_text'] else ''}</b>\n\n"                
                    f" ")
            await send_message_user(bot=bot, content_type=note['content_type'],
                                    content_text=text,
                                    user_id=user_id,
                                    file_id=note['file_id'],
                                    kb=rule_note_kb(note['id']))
        except Exception as E:
            print(f'Error: {E}')
            await asyncio.sleep(2)
        finally:
            await asyncio.sleep(0.5)        