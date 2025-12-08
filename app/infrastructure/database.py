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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS authorizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_id TEXT NOT NULL,
                authorization_id TEXT NOT NULL,
                payment_id TEXT,
                transaction_id TEXT,
                status TEXT NOT NULL,
                type TEXT NOT NULL DEFAULT 'AUTHORIZATION',
                raw_response TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS cancellations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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


def save_authorization(
    merchant_id: str,
    authorization_id: str,
    payment_id: str | None,
    transaction_id: str | None,
    status: str,
    raw_response: dict,
    auth_type: str = "AUTHORIZATION",
):
    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO authorizations (merchant_id, authorization_id, payment_id, transaction_id, status, type, raw_response, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                merchant_id,
                authorization_id,
                payment_id,
                transaction_id,
                status,
                auth_type,
                json.dumps(raw_response),
                created_at,
            ),
        )
        conn.commit()

def save_cancellation(
    payment_id: str,
    transaction_id: str,
    status: str,
    raw_response: dict,
):
    created_at = datetime.utcnow().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO cancellations (payment_id, transaction_id, status, raw_response, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payment_id,
                transaction_id,
                status,
                json.dumps(raw_response),
                created_at,
            ),
        )
        conn.commit()