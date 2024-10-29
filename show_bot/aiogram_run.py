import asyncio
from create_bot import bot, dp, admins
from data_base.base import create_tables
# from handlers.note.find_note_router import find_note_router
# from handlers.note.upd_note_router import upd_note_router
# from handlers.note.add_note_router import add_note_router
from aiogram.types import BotCommand, BotCommandScopeDefault

from handlers.start_router import start_router


# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Функция, которая выполнится когда бот запустится
async def start_bot():
    await set_commands()
    await create_tables()
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, f'Бот запущен.')
        except:
            pass


# Функция, которая выполнится когда бот завершит свою работу
async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен.')
    except:
        pass


async def main():
    # регистрация роутеров
    dp.include_router(start_router)
    # dp.include_router(add_note_router)
    # dp.include_router(find_note_router)
    # dp.include_router(upd_note_router)

    # регистрация функций
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    # запуск бота в режиме long polling при запуске бот очищает все обновления, которые были за его моменты бездействия
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())