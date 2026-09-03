import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent
from aiohttp import web

from config import BOT_TOKEN, WEBHOOK_HOST, WEBHOOK_PORT
from handlers import catalog, common, payment, start
from storage import init_db
from webhook.server import create_webhook_app

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Порядок важен: специфичные роутеры — раньше общего fallback-обработчика.
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(payment.router)
    dp.include_router(common.router)  # ловит всё, что не подошло другим роутерам

    @dp.error()
    async def error_handler(event: ErrorEvent) -> None:
        logger.exception(
            "Ошибка при обработке апдейта %s: %s", event.update, event.exception
        )

    # HTTP-сервер для приёма вебхуков GetCourse — крутится в том же процессе,
    # что и polling бота (отдельный деплой/контейнер не нужен).
    webhook_app = create_webhook_app(bot)
    runner = web.AppRunner(webhook_app)
    await runner.setup()
    site = web.TCPSite(runner, WEBHOOK_HOST, WEBHOOK_PORT)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await site.start()
        logger.info("Приём вебхуков GetCourse: http://%s:%s/getcourse/webhook/<secret>", WEBHOOK_HOST, WEBHOOK_PORT)
        logger.info("Бот запущен, начинаю polling...")
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен.")
