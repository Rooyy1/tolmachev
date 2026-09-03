from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.products import CATEGORIES


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat_key, cat in CATEGORIES.items():
        builder.button(text=cat["title"], callback_data=cat_key)
    builder.button(text="👤 О тренере", callback_data="cat_about")
    builder.adjust(1)
    return builder.as_markup()
