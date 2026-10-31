"""SQLite connection and schema helpers."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "database" / "app.db"
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


class DatabaseConnection(sqlite3.Connection):
    """Connection that also closes when used as a context manager."""

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def get_connection(database_path: str | os.PathLike[str] | None = None) -> sqlite3.Connection:
    """Open a SQLite connection configured for named-column row access."""
    path = database_path or os.environ.get("DATABASE_PATH") or DEFAULT_DATABASE_PATH
    connection = sqlite3.connect(path, factory=DatabaseConnection)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(
    database_path: str | os.PathLike[str] | None = None,
) -> None:
    """Create all application tables and indexes if they do not exist, and migrate missing columns."""
    with get_connection(database_path) as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        
        for sql in (
            "ALTER TABLE Users ADD COLUMN profile_image TEXT",
            "ALTER TABLE Services ADD COLUMN image_path TEXT",
            "ALTER TABLE Categories ADD COLUMN image_path TEXT",
            "ALTER TABLE Users ADD COLUMN is_deleted INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE Services ADD COLUMN is_deleted INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE Categories ADD COLUMN is_deleted INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE Appointments ADD COLUMN is_deleted INTEGER NOT NULL DEFAULT 0",
        ):
            try:
                connection.execute(sql)
            except sqlite3.OperationalError:
                pass  


@contextmanager
def transaction(
    database_path: str | os.PathLike[str] | None = None,
) -> Iterator[sqlite3.Connection]:
    """Yield a connection and commit on success, rolling back on failure."""
    connection = get_connection(database_path)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()