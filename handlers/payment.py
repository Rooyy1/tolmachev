import uuid

from aiogram import Router, F
from aiogram.types import CallbackQuery, User

from config import TRAINER_CHAT_ID
from data.products import PRODUCTS, build_product_card, format_price
from data.texts import (
    PAID_MANUAL_NOTICE_TRAINER,
    PAID_MANUAL_NOTICE_USER,
    PAY_INTRO_TEXT,
    UNKNOWN_PRODUCT_TEXT,
)
from keyboards.main import main_menu_keyboard
from keyboards.product import pay_keyboard
from storage import create_order, get_order

router = Router()


def _mention(user: User) -> str:
    if user.username:
        return f"@{user.username}"
    return f'<a href="tg://user?id={user.id}">{user.full_name}</a>'


@router.callback_query(F.data.startswith("prod_pay_"))
async def start_payment(callback: CallbackQuery) -> None:
    key = callback.data.removeprefix("prod_pay_")
    if key not in PRODUCTS:
        await callback.message.answer(UNKNOWN_PRODUCT_TEXT, reply_markup=main_menu_keyboard())
        await callback.answer()
        return

    product = PRODUCTS[key]
    user = callback.from_user
    order_uid = uuid.uuid4().hex[:12]

    await create_order(
        order_uid=order_uid,
        tg_user_id=user.id,
        tg_username=user.username,
        full_name=user.full_name,
        product_key=key,
    )

    # order_uid прокидывается в GetCourse через GET-параметр — см. README,
    # раздел "Настройка GetCourse", шаг про доп. поле order_uid.
    base_url = product["gc_url"]
    sep = "&" if "?" in base_url else "?"
    pay_url = f"{base_url}{sep}order_uid={order_uid}"

    await callback.message.answer(
        f"{build_product_card(key)}\n\n{PAY_INTRO_TEXT}",
        reply_markup=pay_keyboard(order_uid, pay_url),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("prod_paidmanual_"))
async def paid_manual(callback: CallbackQuery) -> None:
    """Резервная кнопка «Я оплатил»: шлёт тренеру НЕподтверждённое
    уведомление на случай, если вебхук GetCourse ещё не настроен или
    почему-то не дошёл."""
    order_uid = callback.data.removeprefix("prod_paidmanual_")
    order = await get_order(order_uid)

    if order:
        product = PRODUCTS.get(order["product_key"])
        title = product["title"] if product else order["product_key"]
        price = format_price(product["price"]) if product else "—"
    else:
        title, price = "неизвестный товар", "—"

    if TRAINER_CHAT_ID:
        await callback.bot.send_message(
            TRAINER_CHAT_ID,
            PAID_MANUAL_NOTICE_TRAINER.format(
                mention=_mention(callback.from_user), title=title, price=price
            ),
        )

    await callback.message.answer(PAID_MANUAL_NOTICE_USER)
    await callback.answer()
