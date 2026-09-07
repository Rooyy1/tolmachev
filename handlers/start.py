import logging

from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_CHAT_ID, WELCOME_PHOTO_ID
from data import crm
from data.texts import MAIN_MENU_PROMPT, NEW_LEAD_NOTICE, STATS_TEXT, WELCOME_TEXT, WHOAMI_TEXT
from keyboards.main import main_menu_keyboard

router = Router()
logger = logging.getLogger(__name__)


async def send_welcome(message: Message) -> None:
    """Одно цельное приветственное сообщение: фото + весь текст.
    Если WELCOME_PHOTO_ID пустой или невалидный для текущего бота — не
    падаем, а тихо отправляем текст без фото."""
    if WELCOME_PHOTO_ID:
        try:
            await message.answer_photo(
                photo=WELCOME_PHOTO_ID,
                caption=WELCOME_TEXT,
                reply_markup=main_menu_keyboard(),
            )
            return
        except TelegramBadRequest:
            logger.warning("Не удалось отправить фото приветствия, отправляю текст без фото.")

    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


async def _register_lead(message: Message) -> None:
    """CRM: запоминаем пользователя при первом /start и, если это новый
    лид (а не повторный заход), сразу шлём уведомление админу — кто зашёл
    в бота."""
    user = message.from_user
    is_new = crm.register_lead(
        tg_user_id=user.id,
        tg_username=user.username,
        full_name=user.full_name,
    )
    if is_new and ADMIN_CHAT_ID:
        mention = f"@{user.username}" if user.username else user.full_name
        try:
            await message.bot.send_message(
                ADMIN_CHAT_ID, NEW_LEAD_NOTICE.format(mention=mention)
            )
        except Exception:
            logger.exception("Не удалось отправить уведомление о новом лиде админу")


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await _register_lead(message)
    await send_welcome(message)


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    """Вернуться в главное меню в любой момент."""
    await state.clear()
    await message.answer(MAIN_MENU_PROMPT, reply_markup=main_menu_keyboard())


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    """CRM: сколько всего уникальных людей зашло в бота. Отвечает только
    админу (ADMIN_CHAT_ID) — остальным как на любую нераспознанную команду
    промолчит и уйдёт в общий fallback (handlers/common.py)."""
    if message.chat.id != ADMIN_CHAT_ID:
        return
    total = crm.count_leads()
    await message.answer(STATS_TEXT.format(total=total))


@router.message(Command("whoami"))
async def cmd_whoami(message: Message) -> None:
    """Служебная команда: чтобы узнать свой chat_id — он нужен тренеру,
    чтобы вписать TRAINER_CHAT_ID в .env и получать заявки об оплате."""
    await message.answer(
        WHOAMI_TEXT.format(
            chat_id=message.chat.id,
            username=message.from_user.username or "—",
        )
    )


@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.answer(MAIN_MENU_PROMPT, reply_markup=main_menu_keyboard())
    await callback.answer()
