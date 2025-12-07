import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "akua_poc.db"
DB_PATH.parent.mkdir(exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                payment_id TEXT NOT NULL,
                transaction_id TEXT NOT NULL,
                status TEXT NOT NULL,
                raw_response TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_payment(order_id: str, payment_id: str, transaction_id: str, status: str, raw_response: dict):
    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO payments (order_id, payment_id, transaction_id, status, raw_response, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (order_id, payment_id, transaction_id, status, json.dumps(raw_response), created_at),
        )
        conn.commit()