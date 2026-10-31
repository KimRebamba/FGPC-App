"""Appointment model and persistence operations."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from database.db import get_connection


@dataclass(slots=True)
class Appointment:
    appointment_id: int
    user_id: int
    service_id: int
    motorcycle_model: str
    motorcycle_plate: str | None
    appointment_date: str
    appointment_time: str
    price_at_booking: float
    status: str
    customer_notes: str | None
    created_at: str
    updated_at: str | None
    is_deleted: bool = False

    @classmethod
    def from_row(cls, row: sqlite3.Row | dict[str, Any]) -> "Appointment":
        keys = row.keys() if hasattr(row, "keys") else row
        is_del = bool(row["is_deleted"]) if "is_deleted" in keys else False
        clean_time = str(row["appointment_time"]).split("#deleted_")[0]
        return cls(
            row["appointment_id"],
            row["user_id"],
            row["service_id"],
            row["motorcycle_model"],
            row["motorcycle_plate"],
            row["appointment_date"],
            clean_time,
            float(row["price_at_booking"]),
            row["status"],
            row["customer_notes"],
            row["created_at"],
            row["updated_at"],
            is_del,
        )

    @classmethod
    def find_by_id(
        cls, appointment_id: int, database_path: str | None = None
    ) -> "Appointment | None":
        with get_connection(database_path) as connection:
            row = connection.execute(
                "SELECT * FROM Appointments WHERE appointment_id = ?", (appointment_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def list_for_user(
        cls, user_id: int, include_deleted: bool = False, database_path: str | None = None
    ) -> list["Appointment"]:
        query = "SELECT * FROM Appointments WHERE user_id = ?"
        if not include_deleted:
            query += " AND is_deleted = 0"
        query += " ORDER BY appointment_date DESC, appointment_time DESC"
        with get_connection(database_path) as connection:
            rows = connection.execute(query, (user_id,)).fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def list_all(
        cls, include_deleted: bool = False, database_path: str | None = None
    ) -> list["Appointment"]:
        query = "SELECT * FROM Appointments"
        if not include_deleted:
            query += " WHERE is_deleted = 0"
        query += " ORDER BY appointment_date, appointment_time"
        with get_connection(database_path) as connection:
            rows = connection.execute(query).fetchall()
        return [cls.from_row(row) for row in rows]

    @classmethod
    def create(
        cls,
        user_id: int,
        service_id: int,
        motorcycle_model: str,
        appointment_date: str,
        appointment_time: str,
        price_at_booking: float,
        motorcycle_plate: str | None = None,
        customer_notes: str | None = None,
        database_path: str | None = None,
    ) -> "Appointment":
        with get_connection(database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO Appointments
                    (user_id, service_id, motorcycle_model, motorcycle_plate,
                     appointment_date, appointment_time, price_at_booking,
                     customer_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    service_id,
                    motorcycle_model,
                    motorcycle_plate,
                    appointment_date,
                    appointment_time,
                    price_at_booking,
                    customer_notes,
                ),
            )
            row = connection.execute(
                "SELECT * FROM Appointments WHERE appointment_id = ?", (cursor.lastrowid,)
            ).fetchone()
        return cls.from_row(row)

    @classmethod
    def update_status(
        cls,
        appointment_id: int,
        status: str,
        database_path: str | None = None,
    ) -> "Appointment | None":
        with get_connection(database_path) as connection:
            connection.execute(
                """
                UPDATE Appointments
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE appointment_id = ?
                """,
                (status, appointment_id),
            )
            row = connection.execute(
                "SELECT * FROM Appointments WHERE appointment_id = ?", (appointment_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def update(
        cls,
        appointment_id: int,
        appointment_date: str,
        appointment_time: str,
        motorcycle_model: str,
        motorcycle_plate: str | None = None,
        status: str = "pending",
        customer_notes: str | None = None,
        database_path: str | None = None,
    ) -> "Appointment | None":
        with get_connection(database_path) as connection:
            connection.execute(
                """
                UPDATE Appointments
                SET appointment_date = ?, appointment_time = ?, motorcycle_model = ?,
                    motorcycle_plate = ?, status = ?, customer_notes = ?, updated_at = CURRENT_TIMESTAMP
                WHERE appointment_id = ?
                """,
                (
                    appointment_date,
                    appointment_time,
                    motorcycle_model,
                    motorcycle_plate,
                    status,
                    customer_notes,
                    appointment_id,
                ),
            )
            row = connection.execute(
                "SELECT * FROM Appointments WHERE appointment_id = ?", (appointment_id,)
            ).fetchone()
        return cls.from_row(row) if row else None

    @classmethod
    def delete(cls, appointment_id: int, database_path: str | None = None) -> bool:
        """Soft-delete appointment by setting is_deleted = 1 and releasing slot."""
        with get_connection(database_path) as connection:
            cursor = connection.execute(
                """
                UPDATE Appointments
                SET is_deleted = 1,
                    appointment_time = appointment_time || '#deleted_' || appointment_id
                WHERE appointment_id = ? AND is_deleted = 0
                """,
                (appointment_id,),
            )
            return cursor.rowcount > 0

    @classmethod
    def delete_many(cls, appointment_ids: list[int], database_path: str | None = None) -> int:
        """Soft-delete multiple appointments by setting is_deleted = 1 and releasing slot."""
        if not appointment_ids:
            return 0
        with get_connection(database_path) as connection:
            placeholders = ",".join("?" for _ in appointment_ids)
            cursor = connection.execute(
                f"""
                UPDATE Appointments
                SET is_deleted = 1,
                    appointment_time = appointment_time || '#deleted_' || appointment_id
                WHERE appointment_id IN ({placeholders}) AND is_deleted = 0
                """,
                appointment_ids,
            )
            return cursor.rowcount