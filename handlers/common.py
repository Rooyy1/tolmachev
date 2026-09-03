from aiogram import Router
from aiogram.types import CallbackQuery, Message

from data.texts import FALLBACK_CALLBACK_TEXT, FALLBACK_TEXT
from keyboards.main import main_menu_keyboard

# Этот роутер должен быть подключён ПОСЛЕДНИМ в bot.py — он ловит всё,
# что не подошло ни одному специфичному хендлеру.
router = Router()


@router.message()
async def fallback_message(message: Message) -> None:
    await message.answer(FALLBACK_TEXT, reply_markup=main_menu_keyboard())


@router.callback_query()
async def fallback_callback(callback: CallbackQuery) -> None:
    """Устаревшая/неизвестная кнопка — без этого хендлера Telegram будет
    бесконечно крутить "часики" на кнопке."""
    await callback.answer(FALLBACK_CALLBACK_TEXT)
    await callback.message.answer(FALLBACK_TEXT, reply_markup=main_menu_keyboard())
