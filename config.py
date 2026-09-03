import logging
import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Юзернейм тренера — используется только для справки/CTA в текстах.
TRAINER_USERNAME = os.getenv("TRAINER_USERNAME", "tema.evgenevich")

# chat_id тренера в Telegram — именно сюда бот шлёт заявки об оплате.
# Telegram Bot API не умеет слать сообщения "по юзернейму" — нужен числовой
# chat_id. Получить его просто:
#   1. Тренер открывает бота и пишет ему /whoami
#   2. Бот присылает его chat_id
#   3. Этот chat_id вписывается сюда, в .env
TRAINER_CHAT_ID = int(os.getenv("TRAINER_CHAT_ID", "0") or 0)

# --- Приём вебхуков от GetCourse ---
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT = int(os.getenv("WEBHOOK_PORT", "8080"))
# Секретная часть пути вебхука — чтобы посторонний не мог слать боту фейковые
# "заявки об оплате". Придумайте длинную случайную строку.
GETCOURSE_WEBHOOK_SECRET = os.getenv("GETCOURSE_WEBHOOK_SECRET", "change-me")

DB_PATH = os.getenv("DB_PATH", "orders.db")

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
