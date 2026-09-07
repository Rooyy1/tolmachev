"""Простая CRM: кто и когда зашёл в бота (нажал /start).

Нужна для двух вещей:
  1. Уведомление админу о новом лиде (см. handlers/start.py).
  2. Команда /stats — сколько всего уникальных людей был в боте.

Используется встроенный sqlite3 (без новых зависимостей в requirements.txt),
чтобы список не терялся при перезапуске бота — в отличие от словаря/сета
в памяти, который бы обнулялся при каждом деплое.
"""
import sqlite3
from pathlib import Path
from typing import Optional

# Файл лежит рядом с bot.py, в корне проекта.
DB_PATH = Path(__file__).resolve().parent.parent / "crm.db"

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS crm_users (
    tg_user_id INTEGER PRIMARY KEY,
    tg_username TEXT,
    full_name TEXT,
    first_seen TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def init_db() -> None:
    """Вызывается один раз при старте бота (см. bot.py)."""
    with sqlite3.connect(DB_PATH) as db:
        db.execute(_CREATE_SQL)
        db.commit()


def register_lead(tg_user_id: int, tg_username: Optional[str], full_name: str) -> bool:
    """Записывает пользователя в CRM, если его там ещё не было.

    Возвращает True, если это НОВЫЙ лид (значит, нужно отправить
    уведомление админу) — и False, если человек уже жал /start раньше
    (например, повторно зашёл или сделал /menu после рестарта бота).
    """
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.execute(
            "SELECT 1 FROM crm_users WHERE tg_user_id = ?", (tg_user_id,)
        )
        if cursor.fetchone():
            return False
        db.execute(
            "INSERT INTO crm_users (tg_user_id, tg_username, full_name) VALUES (?, ?, ?)",
            (tg_user_id, tg_username, full_name),
        )
        db.commit()
        return True


def count_leads() -> int:
    """Сколько всего уникальных людей когда-либо заходило в бота."""
    with sqlite3.connect(DB_PATH) as db:
        cursor = db.execute("SELECT COUNT(*) FROM crm_users")
        return cursor.fetchone()[0]
