"""Appointment application operations."""

from __future__ import annotations

import datetime
import sqlite3

from models.appointment import Appointment
from models.service import Service
from models.user import User

VALID_STATUSES = {"pending", "confirmed", "completed", "cancelled", "rejected"}


def create_appointment(
    user_id: int,
    service_id: int,
    motorcycle_model: str,
    appointment_date: str,
    appointment_time: str,
    motorcycle_plate: str | None = None,
    customer_notes: str | None = None,
    database_path: str | None = None,
) -> Appointment:
    user = User.find_by_id(user_id, database_path)
    if user is None or getattr(user, "is_deleted", False):
        raise ValueError("User not found.")
    service = Service.find_by_id(service_id, database_path)
    if service is None or getattr(service, "is_deleted", False):
        raise ValueError("Service not found.")
    if not service.is_available:
        raise ValueError("The selected service is not available.")
    if not motorcycle_model.strip():
        raise ValueError("Motorcycle model is required.")
    try:
        parsed_date = datetime.date.fromisoformat(appointment_date)
        parsed_time = datetime.time.fromisoformat(appointment_time)
    except ValueError as error:
        raise ValueError(
            "Appointment date and time must use ISO format."
        ) from error

    today = datetime.date.today()
    max_date = today + datetime.timedelta(days=30)
    if parsed_date < today:
        raise ValueError("Appointment date cannot be in the past.")
    if parsed_date > max_date:
        raise ValueError(
            f"Appointments can only be booked up to 30 days in advance (until {max_date.isoformat()})."
        )
    if parsed_date == today:
        now_time = datetime.datetime.now().time()
        if parsed_time <= now_time:
            raise ValueError("The selected appointment time has already passed today.")
    try:
        return Appointment.create(
            user_id=user_id,
            service_id=service_id,
            motorcycle_model=motorcycle_model.strip(),
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            price_at_booking=service.price,
            motorcycle_plate=motorcycle_plate.strip() if motorcycle_plate else None,
            customer_notes=customer_notes.strip() if customer_notes else None,
            database_path=database_path,
        )
    except sqlite3.IntegrityError as error:
        if "UNIQUE constraint failed: Appointments" in str(error):
            raise ValueError(
                "That service is already booked for the selected date and time."
            ) from error
        raise


def list_user_appointments(
    user_id: int, include_deleted: bool = False, database_path: str | None = None
) -> list[Appointment]:
    return Appointment.list_for_user(user_id, include_deleted, database_path)


def list_appointments(
    include_deleted: bool = False, database_path: str | None = None
) -> list[Appointment]:
    return Appointment.list_all(include_deleted, database_path)


def update_appointment_status(
    appointment_id: int,
    status: str,
    database_path: str | None = None,
) -> Appointment:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid appointment status: {status}")
    appointment = Appointment.update_status(appointment_id, status, database_path)
    if appointment is None:
        raise ValueError("Appointment not found.")
    return appointment


def update_appointment(
    appointment_id: int,
    appointment_date: str,
    appointment_time: str,
    motorcycle_model: str,
    motorcycle_plate: str | None = None,
    status: str = "pending",
    customer_notes: str | None = None,
    database_path: str | None = None,
) -> Appointment:
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid appointment status: {status}")
    if not motorcycle_model.strip():
        raise ValueError("Motorcycle model is required.")
    try:
        datetime.date.fromisoformat(appointment_date)
        datetime.time.fromisoformat(appointment_time)
    except ValueError as error:
        raise ValueError("Appointment date and time must use ISO format.") from error
    appointment = Appointment.update(
        appointment_id=appointment_id,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        motorcycle_model=motorcycle_model.strip(),
        motorcycle_plate=motorcycle_plate.strip() if motorcycle_plate else None,
        status=status,
        customer_notes=customer_notes.strip() if customer_notes else None,
        database_path=database_path,
    )
    if appointment is None:
        raise ValueError("Appointment not found.")
    return appointment


def delete_appointment(appointment_id: int, database_path: str | None = None) -> bool:
    success = Appointment.delete(appointment_id, database_path)
    if not success:
        raise ValueError("Appointment not found or cannot be deleted.")
    return True


def delete_appointments(appointment_ids: list[int], database_path: str | None = None) -> int:
    return Appointment.delete_many(appointment_ids, database_path)