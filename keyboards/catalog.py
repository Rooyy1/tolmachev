from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from data.products import CATEGORIES, PRODUCTS, format_price


def category_products_keyboard(cat_key: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for prod_key in CATEGORIES[cat_key]["products"]:
        p = PRODUCTS[prod_key]
        builder.button(
            text=f"{p['title']} — {format_price(p['price'])}",
            callback_data=f"prod_view_{prod_key}",
        )
    builder.button(text="⬅️ В начало", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()
