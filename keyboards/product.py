from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def product_keyboard(key: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Оплатить", callback_data=f"prod_pay_{key}")
    builder.button(text="⬅️ Назад", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()


def pay_keyboard(order_uid: str, pay_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Перейти к оплате", url=pay_url)
    builder.button(text="✅ Я оплатил", callback_data=f"prod_paidmanual_{order_uid}")
    builder.button(text="⬅️ В начало", callback_data="back_main")
    builder.adjust(1)
    return builder.as_markup()
