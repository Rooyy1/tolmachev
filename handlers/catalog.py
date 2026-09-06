import logging

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from config import WELCOME_PHOTO_ID
from data.products import CATEGORIES, PRODUCTS, build_product_card
from data.texts import ABOUT_TEXT, ONLINE_INTRO, UNKNOWN_PRODUCT_TEXT
from keyboards.catalog import category_products_keyboard
from keyboards.main import main_menu_keyboard
from keyboards.product import product_keyboard

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "cat_about")
async def show_about(callback: CallbackQuery) -> None:
    """Та же приветственная фотография, что и в /start — чтобы карточка
    "О тренере" выглядела так же, а не голым текстом."""
    if WELCOME_PHOTO_ID:
        try:
            await callback.message.answer_photo(
                photo=WELCOME_PHOTO_ID,
                caption=ABOUT_TEXT,
                reply_markup=main_menu_keyboard(),
            )
            await callback.answer()
            return
        except TelegramBadRequest:
            logger.warning("Не удалось отправить фото для \"О тренере\", отправляю текст.")

    await callback.message.answer(ABOUT_TEXT, reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data.in_(CATEGORIES.keys()))
async def show_category(callback: CallbackQuery) -> None:
    cat_key = callback.data
    cat = CATEGORIES[cat_key]
    intro = ONLINE_INTRO if cat_key == "cat_online" else f"<b>{cat['title']}</b>\n\n{cat['desc']}"
    await callback.message.answer(intro, reply_markup=category_products_keyboard(cat_key))
    await callback.answer()


@router.callback_query(F.data.startswith("prod_view_"))
async def show_product(callback: CallbackQuery) -> None:
    """Карточка товара: креатив (фото) + описание + кнопки под ним.
    Если фото по какой-то причине не отправляется (например, file_id
    привязан к другому боту) — тихо откатываемся на текстовую карточку,
    чтобы пользователь в любом случае не остался без ответа."""
    key = callback.data.removeprefix("prod_view_")
    if key not in PRODUCTS:
        await callback.message.answer(UNKNOWN_PRODUCT_TEXT, reply_markup=main_menu_keyboard())
        await callback.answer()
        return

    product = PRODUCTS[key]
    caption = build_product_card(key)
    photo = product.get("photo")

    if photo:
        try:
            await callback.message.answer_photo(
                photo=photo, caption=caption, reply_markup=product_keyboard(key)
            )
            await callback.answer()
            return
        except TelegramBadRequest:
            logger.warning("Не удалось отправить фото для товара %s, отправляю текст.", key)

    await callback.message.answer(caption, reply_markup=product_keyboard(key))
    await callback.answer()
