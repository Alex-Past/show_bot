import sqlite3
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.shop_keyboard import shop_kb

router = Router()

# Создаём соединение с базой данных
conn = sqlite3.connect("shopping_list.db")
cursor = conn.cursor()

# Создаём таблицу, если её нет
cursor.execute("""
    CREATE TABLE IF NOT EXISTS shopping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT NOT NULL
    )
""")
conn.commit()


@router.message(Command("start"))
async def add_item(message: Message):
    text = 'Привет привет! Что запишем?'
    await message.answer(text, reply_markup=shop_kb())


@router.message(F.text == "Список покупок")
async def show_list(message: Message):
    cursor.execute("SELECT item FROM shopping")
    items = cursor.fetchall()
    if items:
        shopping_text = "\n".join(
            f"{index + 1}. {item[0]}" for index, item in enumerate(items))
        await message.answer(shopping_text)
    else:
        await message.answer("Список пуст.")


@router.message(F.text == "Очистить список")
async def clear_list(message: Message):
    cursor.execute("DELETE FROM shopping")
    conn.commit()
    await message.answer("Список успешно очищен!")


@router.message()
async def add_item(message: Message):
    if not message.text.startswith("/"):
        cursor.execute("INSERT INTO shopping (item) VALUES (?)",
                       (message.text,))
        conn.commit()
        await message.answer(f"Добавлено: {message.text}", reply_markup=shop_kb())
    else:
        await message.answer("Добавьте что-нибудь в корзину!")
