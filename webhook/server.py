"""Приём вебхуков от GetCourse об успешной оплате.

GetCourse должен быть настроен на отправку вебхука (в личном кабинете:
Интеграции → Вебхуки, или Аккаунт → Настройки → Уведомления, в зависимости
от версии интерфейса) на адрес:

    https://ВАШ_ДОМЕН/getcourse/webhook/<GETCOURSE_WEBHOOK_SECRET>

по событию "Оплата заказа" / "Изменение статуса заказа на оплаченный".
Подробная пошаговая настройка — в README.md, раздел "Настройка GetCourse".

ВАЖНО: точная структура JSON, который присылает GetCourse, немного
отличается в зависимости от настроек аккаунта и версии GetCourse.
Ниже — гибкий парсер, который рекурсивно ищет order_uid в теле запроса,
поэтому конкретный формат вложенности (user/order/deal/...) не важен.
Если заказ всё же не находится — в логах бота будет виден весь payload
(смотрите строку "GetCourse webhook payload"), по нему легко понять,
куда GetCourse на самом деле кладёт значение доп. поля order_uid.
"""
import json
import logging
from typing import Optional

from aiohttp import web

from config import GETCOURSE_WEBHOOK_SECRET, TRAINER_CHAT_ID
from data.products import PRODUCTS, format_price
from data.texts import AUTO_PAID_NOTICE_TRAINER, AUTO_PAID_NOTICE_USER
from storage import get_order, mark_notified

logger = logging.getLogger(__name__)


def _find_order_uid(payload: dict) -> Optional[str]:
    """Рекурсивно ищет значение доп. поля order_uid где бы GetCourse его
    ни положил (user.order_uid, order.custom_fields.order_uid и т.п.)."""
    found = []

    def walk(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, str) and "order_uid" in key.lower():
                    found.append(value)
                walk(value)
        elif isinstance(obj, list):
            for item in obj:
                walk(item)

    walk(payload)
    return found[0] if found else None


async def _parse_payload(request: web.Request) -> dict:
    raw = await request.read()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # GetCourse нередко шлёт form-urlencoded, где значения полей — сами
    # являются JSON-строками (например params=%7B...%7D).
    form = await request.post()
    payload = {}
    for key, value in form.items():
        try:
            payload[key] = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            payload[key] = value
    return payload


async def handle_webhook(request: web.Request) -> web.Response:
    secret = request.match_info.get("secret")
    if secret != GETCOURSE_WEBHOOK_SECRET:
        return web.json_response({"ok": False, "error": "bad secret"}, status=403)

    payload = await _parse_payload(request)
    logger.info("GetCourse webhook payload: %s", payload)

    order_uid = _find_order_uid(payload)
    if not order_uid:
        logger.warning(
            "Не удалось найти order_uid в вебхуке GetCourse — см. payload выше "
            "и сверьте с README (доп. поле order_uid должно быть проброшено)."
        )
        return web.json_response({"ok": True, "warning": "order_uid not found"})

    order = await get_order(order_uid)
    if not order:
        logger.warning("order_uid %s не найден в локальной базе заявок.", order_uid)
        return web.json_response({"ok": True, "warning": "order not found in db"})

    if order["notified"]:
        # Защита от повторных вебхуков по одной и той же оплате.
        return web.json_response({"ok": True, "info": "already notified"})

    bot = request.app["bot"]
    product = PRODUCTS.get(order["product_key"])
    title = product["title"] if product else order["product_key"]
    price = format_price(product["price"]) if product else "—"
    mention = f"@{order['tg_username']}" if order["tg_username"] else order["full_name"]

    if TRAINER_CHAT_ID:
        await bot.send_message(
            TRAINER_CHAT_ID,
            AUTO_PAID_NOTICE_TRAINER.format(
                mention=mention, title=title, price=price, order_uid=order_uid
            ),
        )
    else:
        logger.warning("TRAINER_CHAT_ID не задан — некому отправить уведомление об оплате.")

    try:
        await bot.send_message(order["tg_user_id"], AUTO_PAID_NOTICE_USER.format(title=title))
    except Exception:
        logger.exception(
            "Не удалось отправить подтверждение оплаты пользователю %s", order["tg_user_id"]
        )

    await mark_notified(order_uid)
    return web.json_response({"ok": True})


def create_webhook_app(bot) -> web.Application:
    app = web.Application()
    app["bot"] = bot
    app.router.add_post("/getcourse/webhook/{secret}", handle_webhook)
    return app
