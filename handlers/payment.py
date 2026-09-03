from aiogram import Router, F
from aiogram.types import CallbackQuery, User

from config import TRAINER_CHAT_ID
from data.products import PRODUCTS, build_product_card, format_price
from data.texts import (
    PAID_NOTICE_TRAINER,
    PAID_NOTICE_USER,
    PAYMENT_REQUISITES_TEXT,
    UNKNOWN_PRODUCT_TEXT,
)
from keyboards.main import main_menu_keyboard
from keyboards.product import pay_keyboard

router = Router()


def _mention(user: User) -> str:
    if user.username:
        return f"@{user.username}"
    return f'<a href="tg://user?id={user.id}">{user.full_name}</a>'


@router.callback_query(F.data.startswith("prod_pay_"))
async def start_payment(callback: CallbackQuery) -> None:
    """Показываем реквизиты для оплаты и кнопку "Я оплатил"."""
    key = callback.data.removeprefix("prod_pay_")
    if key not in PRODUCTS:
        await callback.message.answer(UNKNOWN_PRODUCT_TEXT, reply_markup=main_menu_keyboard())
        await callback.answer()
        return

    await callback.message.answer(
        f"{build_product_card(key)}\n\n{PAYMENT_REQUISITES_TEXT}",
        reply_markup=pay_keyboard(key),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prod_paid_"))
async def confirm_paid(callback: CallbackQuery) -> None:
    """Клиент сам подтвердил оплату — сразу шлём тренеру заявку:
    username, имя, товар, статус "Оплачено"."""
    key = callback.data.removeprefix("prod_paid_")
    product = PRODUCTS.get(key)
    title = product["title"] if product else key
    price = format_price(product["price"]) if product else "—"
    user = callback.from_user

    if TRAINER_CHAT_ID:
        await callback.bot.send_message(
            TRAINER_CHAT_ID,
            PAID_NOTICE_TRAINER.format(
                mention=_mention(user),
                full_name=user.full_name,
                title=title,
                price=price,
            ),
        )

    await callback.message.answer(PAID_NOTICE_USER)
    await callback.answer()
