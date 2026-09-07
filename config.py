import logging
import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Юзернейм тренера — используется только для справки в текстах.
TRAINER_USERNAME = os.getenv("TRAINER_USERNAME", "tema.evgenevich")

# chat_id тренера в Telegram — именно сюда бот шлёт заявки об оплате.
# Telegram Bot API не умеет слать сообщения "по юзернейму" — нужен числовой
# chat_id. Получить его просто:
#   1. Тренер открывает бота и пишет ему /whoami
#   2. Бот присылает его chat_id
#   3. Этот chat_id вписывается сюда, в .env
TRAINER_CHAT_ID = int(os.getenv("TRAINER_CHAT_ID", "0") or 0)

# chat_id админа для CRM: сюда бот шлёт "🆕 Новый лид" при каждом первом
# заходе нового пользователя, и только этому chat_id отвечает на /stats.
# По умолчанию — фиксированный chat_id, можно переопределить через .env.
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "8913576204") or 0)

# file_id фотографии для приветственного сообщения (/start).
# ВНИМАНИЕ: file_id привязан к конкретному боту, который изначально принял
# это фото. Если используется другой BOT_TOKEN — file_id может не сработать,
# в этом случае бот тихо отправит приветствие без фото (см. handlers/start.py).
WELCOME_PHOTO_ID = os.getenv(
    "WELCOME_PHOTO_ID",
    "AgACAgIAAxkBAANHap3abUBoWdf-BSPQxJcHDiLAzXEAAqEoaxtrt_FIX-xsL-BazEgBAAMCAAN5AAM9BA",
)

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не задан. Скопируйте .env.example в .env и укажите токен, "
        "полученный у @BotFather."
    )

if not TRAINER_CHAT_ID:
    logging.getLogger(__name__).warning(
        "TRAINER_CHAT_ID не задан — уведомления об оплате отправлять будет некому. "
        "Попросите тренера написать боту /whoami и впишите chat_id в .env"
    )
