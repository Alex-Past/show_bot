from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def shop_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Список покупок")
    kb.button(text="Очистить список")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)
