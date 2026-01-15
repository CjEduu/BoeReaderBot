"""SQLite storage for bot data."""

import sqlite3
from datetime import datetime
from pathlib import Path

DATABASE_FILE = Path("data/bot.db")


def _get_connection() -> sqlite3.Connection:
    """Get a database connection, creating the database if needed."""
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """Initialize the database schema."""
    conn = _get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id INTEGER PRIMARY KEY,
                registered_at TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def load_subscribers() -> set[int]:
    """Load all registered subscriber chat IDs."""
    init_database()
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT chat_id FROM subscribers")
        return {row["chat_id"] for row in cursor.fetchall()}
    finally:
        conn.close()


def add_subscriber(chat_id: int) -> bool:
    """
    Add a subscriber to the database.

    Returns:
        True if added, False if already exists.
    """
    init_database()
    conn = _get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO subscribers (chat_id, registered_at) VALUES (?, ?)",
            (chat_id, datetime.now().isoformat())
        )
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()


def remove_subscriber(chat_id: int) -> bool:
    """
    Remove a subscriber from the database.

    Returns:
        True if removed, False if didn't exist.
    """
    init_database()
    conn = _get_connection()
    try:
        conn.execute("DELETE FROM subscribers WHERE chat_id = ?", (chat_id,))
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()


def is_subscriber(chat_id: int) -> bool:
    """Check if a chat_id is registered as a subscriber."""
    init_database()
    conn = _get_connection()
    try:
        cursor = conn.execute(
            "SELECT 1 FROM subscribers WHERE chat_id = ?", (chat_id,)
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()


def get_subscriber_count() -> int:
    """Get the total number of subscribers."""
    init_database()
    conn = _get_connection()
    try:
        cursor = conn.execute("SELECT COUNT(*) as count FROM subscribers")
        return cursor.fetchone()["count"]
    finally:
        conn.close()
