"""Service image model and persistence operations."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from database.db import get_connection


@dataclass(slots=True)
class ServiceImage:
    image_id: int
    service_id: int
    image_path: str
    is_primary: bool
    created_at: str

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any]) -> "ServiceImage":
        return cls(
            row["image_id"],
            row["service_id"],
            row["image_path"],
            bool(row["is_primary"]),
            row["created_at"],
        )

    @classmethod
    def list_for_service(
        cls, service_id: int, database_path: str | None = None
    ) -> list["ServiceImage"]:
        with get_connection(database_path) as connection:
            rows = connection.execute(
                "SELECT * FROM ServiceImages WHERE service_id = ? ORDER BY is_primary DESC, image_id",
                (service_id,),
            ).fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def create(
        cls,
        service_id: int,
        image_path: str,
        is_primary: bool = False,
        database_path: str | None = None,
    ) -> "ServiceImage":
        with get_connection(database_path) as connection:
            if is_primary:
                connection.execute(
                    "UPDATE ServiceImages SET is_primary = 0 WHERE service_id = ?",
                    (service_id,),
                )
            cursor = connection.execute(
                """
                INSERT INTO ServiceImages (service_id, image_path, is_primary)
                VALUES (?, ?, ?)
                """,
                (service_id, image_path, int(is_primary)),
            )
            row = connection.execute(
                "SELECT * FROM ServiceImages WHERE image_id = ?", (cursor.lastrowid,)
            ).fetchone()
        return cls.from_row(row)