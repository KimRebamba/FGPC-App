"""User model and persistence operations."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from database.db import get_connection


@dataclass(slots=True)
class User:
    user_id: int
    first_name: str
    last_name: str
    address: str | None
    contact_number: str | None
    email: str
    password_hash: str
    role: str
    is_active: bool
    created_at: str
    profile_image: str | None = None
    is_deleted: bool = False

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any]) -> "User":
        keys = row.keys() if hasattr(row, "keys") else row
        profile_img = row["profile_image"] if "profile_image" in keys else None
        is_del = bool(row["is_deleted"]) if "is_deleted" in keys else False
        clean_email = str(row["email"]).split("#deleted_")[0]
        return cls(
            user_id=row["user_id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            address=row["address"],
            contact_number=row["contact_number"],
            email=clean_email,
            password_hash=row["password_hash"],
            role=row["role"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            profile_image=profile_img,
            is_deleted=is_del,
        )

    @classmethod
    def find_by_id(cls, user_id: int, database_path: str | None = None) -> "User | None":
        with get_connection(database_path) as connection:
            row = connection.execute(
                "SELECT * FROM Users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def find_by_email(cls, email: str, database_path: str | None = None) -> "User | None":
        with get_connection(database_path) as connection:
            row = connection.execute(
                "SELECT * FROM Users WHERE email = ? AND is_deleted = 0", (email,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def list_all(
        cls, include_deleted: bool = False, database_path: str | None = None
    ) -> list["User"]:
        query = "SELECT * FROM Users"
        if not include_deleted:
            query += " WHERE is_deleted = 0"
        query += " ORDER BY user_id DESC"
        with get_connection(database_path) as connection:
            rows = connection.execute(query).fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def create(
        cls,
        first_name: str,
        last_name: str,
        email: str,
        password_hash: str,
        address: str | None = None,
        contact_number: str | None = None,
        role: str = "customer",
        profile_image: str | None = None,
        database_path: str | None = None,
    ) -> "User":
        with get_connection(database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO Users
                    (first_name, last_name, address, contact_number, email,
                     password_hash, role, profile_image)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    first_name,
                    last_name,
                    address,
                    contact_number,
                    email,
                    password_hash,
                    role,
                    profile_image,
                ),
            )
            row = connection.execute(
                "SELECT * FROM Users WHERE user_id = ?", (cursor.lastrowid,)
            ).fetchone()
        return cls.from_row(row)

    def update_profile(
        self,
        *,
        first_name: str,
        last_name: str,
        address: str | None,
        contact_number: str | None,
        profile_image: str | None = None,
        database_path: str | None = None,
    ) -> "User":
        with get_connection(database_path) as connection:
            if profile_image is not None:
                connection.execute(
                    """
                    UPDATE Users
                    SET first_name = ?, last_name = ?, address = ?, contact_number = ?, profile_image = ?
                    WHERE user_id = ?
                    """,
                    (first_name, last_name, address, contact_number, profile_image, self.user_id),
                )
            else:
                connection.execute(
                    """
                    UPDATE Users
                    SET first_name = ?, last_name = ?, address = ?, contact_number = ?
                    WHERE user_id = ?
                    """,
                    (first_name, last_name, address, contact_number, self.user_id),
                )
            row = connection.execute(
                "SELECT * FROM Users WHERE user_id = ?", (self.user_id,)
            ).fetchone()
        return self.from_row(row)

    @classmethod
    def admin_update(
        cls,
        user_id: int,
        first_name: str,
        last_name: str,
        email: str,
        role: str,
        is_active: bool,
        address: str | None = None,
        contact_number: str | None = None,
        profile_image: str | None = None,
        database_path: str | None = None,
    ) -> "User | None":
        with get_connection(database_path) as connection:
            if profile_image is not None:
                connection.execute(
                    """
                    UPDATE Users
                    SET first_name = ?, last_name = ?, email = ?, role = ?,
                        is_active = ?, address = ?, contact_number = ?, profile_image = ?
                    WHERE user_id = ?
                    """,
                    (
                        first_name,
                        last_name,
                        email,
                        role,
                        int(is_active),
                        address,
                        contact_number,
                        profile_image,
                        user_id,
                    ),
                )
            else:
                connection.execute(
                    """
                    UPDATE Users
                    SET first_name = ?, last_name = ?, email = ?, role = ?,
                        is_active = ?, address = ?, contact_number = ?
                    WHERE user_id = ?
                    """,
                    (
                        first_name,
                        last_name,
                        email,
                        role,
                        int(is_active),
                        address,
                        contact_number,
                        user_id,
                    ),
                )
            row = connection.execute(
                "SELECT * FROM Users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def set_active(
        cls, user_id: int, is_active: bool, database_path: str | None = None
    ) -> "User | None":
        with get_connection(database_path) as connection:
            connection.execute(
                "UPDATE Users SET is_active = ? WHERE user_id = ?",
                (int(is_active), user_id),
            )
            row = connection.execute(
                "SELECT * FROM Users WHERE user_id = ?", (user_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def update_password(
        cls, user_id: int, new_password_hash: str, database_path: str | None = None
    ) -> bool:
        with get_connection(database_path) as connection:
            cursor = connection.execute(
                "UPDATE Users SET password_hash = ? WHERE user_id = ?",
                (new_password_hash, user_id),
            )
            return cursor.rowcount > 0

    @classmethod
    def delete(cls, user_id: int, database_path: str | None = None) -> bool:
        """Soft-delete the user: mark is_deleted = 1 and inactive, preserving all appointments."""
        with get_connection(database_path) as connection:
            cursor = connection.execute(
                """
                UPDATE Users
                SET is_deleted = 1, is_active = 0,
                    email = email || '#deleted_' || user_id
                WHERE user_id = ? AND is_deleted = 0
                """,
                (user_id,),
            )
            return cursor.rowcount > 0

    @classmethod
    def delete_many(cls, user_ids: list[int], database_path: str | None = None) -> int:
        """Soft-delete multiple users: mark is_deleted = 1 and inactive, preserving all appointments."""
        if not user_ids:
            return 0
        with get_connection(database_path) as connection:
            placeholders = ",".join("?" for _ in user_ids)
            cursor = connection.execute(
                f"""
                UPDATE Users
                SET is_deleted = 1, is_active = 0,
                    email = email || '#deleted_' || user_id
                WHERE user_id IN ({placeholders}) AND is_deleted = 0
                """,
                user_ids,
            )
            return cursor.rowcount