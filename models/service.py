"""Service model and persistence operations."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from database.db import get_connection


@dataclass(slots=True)
class Service:
    service_id: int
    category_id: int
    service_name: str
    description: str | None
    price: float
    duration_minutes: int
    is_available: bool
    created_at: str
    image_path: str | None = None
    is_deleted: bool = False

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any]) -> "Service":
        keys = row.keys() if hasattr(row, "keys") else row
        img_path = row["image_path"] if "image_path" in keys else None
        is_del = bool(row["is_deleted"]) if "is_deleted" in keys else False
        return cls(
            row["service_id"],
            row["category_id"],
            row["service_name"],
            row["description"],
            float(row["price"]),
            row["duration_minutes"],
            bool(row["is_available"]),
            row["created_at"],
            img_path,
            is_del,
        )

    @classmethod
    def find_by_id(cls, service_id: int, database_path: str | None = None) -> "Service | None":
        with get_connection(database_path) as connection:
            row = connection.execute(
                "SELECT * FROM Services WHERE service_id = ?", (service_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def list_all(
        cls,
        category_id: int | None = None,
        available_only: bool = False,
        include_deleted: bool = False,
        database_path: str | None = None,
    ) -> list["Service"]:
        conditions: list[str] = []
        parameters: list[Any] = []
        if not include_deleted:
            conditions.append("is_deleted = 0")
        if category_id is not None:
            conditions.append("category_id = ?")
            parameters.append(category_id)
        if available_only:
            conditions.append("is_available = 1")
        query = "SELECT * FROM Services"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY service_id DESC"
        with get_connection(database_path) as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def create(
        cls,
        category_id: int,
        service_name: str,
        price: float,
        duration_minutes: int,
        description: str | None = None,
        image_path: str | None = None,
        database_path: str | None = None,
    ) -> "Service":
        with get_connection(database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO Services
                    (category_id, service_name, description, price, duration_minutes, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (category_id, service_name, description, price, duration_minutes, image_path),
            )
            row = connection.execute(
                "SELECT * FROM Services WHERE service_id = ?", (cursor.lastrowid,)
            ).fetchone()
        return cls.from_row(row)

    @classmethod
    def update(
        cls,
        service_id: int,
        category_id: int,
        service_name: str,
        price: float,
        duration_minutes: int,
        description: str | None = None,
        image_path: str | None = None,
        database_path: str | None = None,
    ) -> "Service | None":
        with get_connection(database_path) as connection:
            if image_path is not None:
                connection.execute(
                    """
                    UPDATE Services
                    SET category_id = ?, service_name = ?, price = ?,
                        duration_minutes = ?, description = ?, image_path = ?
                    WHERE service_id = ?
                    """,
                    (category_id, service_name, price, duration_minutes, description, image_path, service_id),
                )
            else:
                connection.execute(
                    """
                    UPDATE Services
                    SET category_id = ?, service_name = ?, price = ?,
                        duration_minutes = ?, description = ?
                    WHERE service_id = ?
                    """,
                    (category_id, service_name, price, duration_minutes, description, service_id),
                )
            row = connection.execute(
                "SELECT * FROM Services WHERE service_id = ?", (service_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def set_available(
        cls, service_id: int, is_available: bool, database_path: str | None = None
    ) -> "Service | None":
        with get_connection(database_path) as connection:
            connection.execute(
                "UPDATE Services SET is_available = ? WHERE service_id = ?",
                (int(is_available), service_id),
            )
            row = connection.execute(
                "SELECT * FROM Services WHERE service_id = ?", (service_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def delete(cls, service_id: int, database_path: str | None = None) -> bool:
        """Soft-delete the service: mark is_deleted = 1 and unavailable, preserving all bookings."""
        with get_connection(database_path) as connection:
            cursor = connection.execute(
                "UPDATE Services SET is_deleted = 1, is_available = 0 WHERE service_id = ?",
                (service_id,),
            )
            return cursor.rowcount > 0

    @classmethod
    def delete_many(cls, service_ids: list[int], database_path: str | None = None) -> int:
        """Soft-delete multiple services: mark is_deleted = 1 and unavailable, preserving all bookings."""
        if not service_ids:
            return 0
        with get_connection(database_path) as connection:
            placeholders = ",".join("?" for _ in service_ids)
            cursor = connection.execute(
                f"UPDATE Services SET is_deleted = 1, is_available = 0 WHERE service_id IN ({placeholders})",
                service_ids,
            )
            return cursor.rowcount