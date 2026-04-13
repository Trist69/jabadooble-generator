"""
Lightweight SQLite-backed settings store.

Stores key/value pairs in a single table.  No ORM — plain sqlite3
from the standard library so no extra dependencies are needed.

The database file lives in DATA_DIR (Docker volume) and persists
across container restarts.  Secrets (like API keys) are stored here
and never baked into the image.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from threading import Lock

_DB_PATH = Path(os.getenv("DATA_DIR", "/app/data")) / "settings.db"
_lock = Lock()

_DDL = """
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT DEFAULT (datetime('now'))
);
"""


@contextmanager
def _conn():
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    con.row_factory = sqlite3.Row
    try:
        con.execute(_DDL)
        con.commit()
        yield con
    finally:
        con.close()


def get(key: str, default: str | None = None) -> str | None:
    with _lock, _conn() as con:
        row = con.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


def set(key: str, value: str) -> None:  # noqa: A001
    with _lock, _conn() as con:
        con.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)"
            " ON CONFLICT(key) DO UPDATE SET value = excluded.value,"
            " updated_at = datetime('now')",
            (key, value),
        )
        con.commit()


def delete(key: str) -> None:
    with _lock, _conn() as con:
        con.execute("DELETE FROM settings WHERE key = ?", (key,))
        con.commit()


def all_settings() -> dict[str, str]:
    with _lock, _conn() as con:
        rows = con.execute("SELECT key, value FROM settings").fetchall()
    return {row["key"]: row["value"] for row in rows}
