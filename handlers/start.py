from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from data.texts import MAIN_MENU_PROMPT, WELCOME_TEXT, WHOAMI_TEXT
from keyboards.main import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    """Вернуться в главное меню в любой момент."""
    await state.clear()
    await message.answer(MAIN_MENU_PROMPT, reply_markup=main_menu_keyboard())


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
