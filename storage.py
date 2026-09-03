"""Хранилище заявок на оплату.

Когда пользователь жмёт «Оплатить», создаём запись с уникальным order_uid
и его Telegram-данными. Этот order_uid передаётся в ссылку GetCourse
GET-параметром и должен вернуться в вебхуке при успешной оплате — так мы
узнаём, кто именно и что купил.

SQLite выбран, чтобы заявки не терялись при перезапуске бота (в отличие от
словаря в памяти).
"""
from typing import Optional

import aiosqlite

from config import DB_PATH

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    order_uid TEXT PRIMARY KEY,
    tg_user_id INTEGER NOT NULL,
    tg_username TEXT,
    full_name TEXT,
    product_key TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    notified INTEGER DEFAULT 0
);
"""


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(_CREATE_SQL)
        await db.commit()


async def create_order(
    order_uid: str,
    tg_user_id: int,
    tg_username: Optional[str],
    full_name: str,
    product_key: str,
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO orders (order_uid, tg_user_id, tg_username, full_name, product_key) "
            "VALUES (?, ?, ?, ?, ?)",
            (order_uid, tg_user_id, tg_username, full_name, product_key),
        )
        await db.commit()


async def get_order(order_uid: str) -> Optional[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM orders WHERE order_uid = ?", (order_uid,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def mark_notified(order_uid: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE orders SET notified = 1 WHERE order_uid = ?", (order_uid,))
        await db.commit()
