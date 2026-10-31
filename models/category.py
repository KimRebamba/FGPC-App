"""Category model and persistence operations."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from database.db import get_connection


@dataclass(slots=True)
class Category:
    category_id: int
    category_name: str
    description: str | None
    image_path: str | None
    is_active: bool
    is_deleted: bool = False

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any]) -> "Category":
        keys = row.keys() if hasattr(row, "keys") else row
        img_path = row["image_path"] if "image_path" in keys else None
        is_del = bool(row["is_deleted"]) if "is_deleted" in keys else False
        clean_name = str(row["category_name"]).split("#deleted_")[0]
        return cls(
            row["category_id"],
            clean_name,
            row["description"],
            img_path,
            bool(row["is_active"]),
            is_del,
        )

    @classmethod
    def find_by_id(cls, category_id: int, database_path: str | None = None) -> "Category | None":
        with get_connection(database_path) as connection:
            row = connection.execute(
                "SELECT * FROM Categories WHERE category_id = ?", (category_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def list_all(
        cls,
        active_only: bool = False,
        include_deleted: bool = False,
        database_path: str | None = None,
    ) -> list["Category"]:
        conditions: list[str] = []
        if not include_deleted:
            conditions.append("is_deleted = 0")
        if active_only:
            conditions.append("is_active = 1")
        query = "SELECT * FROM Categories"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY category_name"
        with get_connection(database_path) as connection:
            rows = connection.execute(query).fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def create(
        cls,
        category_name: str,
        description: str | None = None,
        image_path: str | None = None,
        database_path: str | None = None,
    ) -> "Category":
        with get_connection(database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO Categories (category_name, description, image_path)
                VALUES (?, ?, ?)
                """,
                (category_name, description, image_path),
            )
            row = connection.execute(
                "SELECT * FROM Categories WHERE category_id = ?", (cursor.lastrowid,)
            ).fetchone()
        return cls.from_row(row)

    @classmethod
    def set_active(
        cls, category_id: int, is_active: bool, database_path: str | None = None
    ) -> "Category | None":
        with get_connection(database_path) as connection:
            connection.execute(
                "UPDATE Categories SET is_active = ? WHERE category_id = ?",
                (int(is_active), category_id),
            )
            row = connection.execute(
                "SELECT * FROM Categories WHERE category_id = ?", (category_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def update(
        cls,
        category_id: int,
        category_name: str,
        description: str | None = None,
        image_path: str | None = None,
        database_path: str | None = None,
    ) -> "Category | None":
        with get_connection(database_path) as connection:
            if image_path is not None:
                connection.execute(
                    """
                    UPDATE Categories
                    SET category_name = ?, description = ?, image_path = ?
                    WHERE category_id = ?
                    """,
                    (category_name, description, image_path, category_id),
                )
            else:
                connection.execute(
                    """
                    UPDATE Categories
                    SET category_name = ?, description = ?
                    WHERE category_id = ?
                    """,
                    (category_name, description, category_id),
                )
            row = connection.execute(
                "SELECT * FROM Categories WHERE category_id = ?", (category_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def delete(cls, category_id: int, database_path: str | None = None) -> bool:
        """Soft-delete category and its services, preserving all historical appointments."""
        with get_connection(database_path) as connection:
            connection.execute(
                "UPDATE Services SET is_deleted = 1, is_available = 0 WHERE category_id = ?",
                (category_id,),
            )
            cursor = connection.execute(
                """
                UPDATE Categories
                SET is_deleted = 1, is_active = 0,
                    category_name = category_name || '#deleted_' || category_id
                WHERE category_id = ? AND is_deleted = 0
                """,
                (category_id,),
            )
            return cursor.rowcount > 0

    @classmethod
    def delete_many(cls, category_ids: list[int], database_path: str | None = None) -> int:
        """Soft-delete multiple categories and their services, preserving all historical appointments."""
        if not category_ids:
            return 0
        with get_connection(database_path) as connection:
            c_placeholders = ",".join("?" for _ in category_ids)
            connection.execute(
                f"UPDATE Services SET is_deleted = 1, is_available = 0 WHERE category_id IN ({c_placeholders})",
                category_ids,
            )
            cursor = connection.execute(
                f"""
                UPDATE Categories
                SET is_deleted = 1, is_active = 0,
                    category_name = category_name || '#deleted_' || category_id
                WHERE category_id IN ({c_placeholders}) AND is_deleted = 0
                """,
                category_ids,
            )
            return cursor.rowcount