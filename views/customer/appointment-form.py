"""Tkinter appointment booking form."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from controllers.appointment_controller import create_appointment
from controllers.service_controller import list_services
from models.user import User
from views.common import labeled_entry, show_error


def create_appointment_form(
    parent: tk.Misc,
    user: User,
    database_path: str | None = None,
) -> ttk.Frame:
    frame = ttk.Frame(parent, padding=12)
    frame.pack(fill="both", expand=True)
    services = list_services(available_only=True, database_path=database_path)
    if not services:
        ttk.Label(frame, text="No services are currently available.").pack()
        return frame

    ttk.Label(frame, text="Service").grid(row=0, column=0, sticky="w", pady=5)
    service_box = ttk.Combobox(
        frame,
        state="readonly",
        values=[f"{service.service_id}: {service.service_name}" for service in services],
        width=35,
    )
    service_box.current(0)
    service_box.grid(row=0, column=1, pady=5)
    date = labeled_entry(frame, "Date (YYYY-MM-DD)", 1)
    time = labeled_entry(frame, "Time (HH:MM)", 2)
    motorcycle = labeled_entry(frame, "Motorcycle model", 3)
    plate = labeled_entry(frame, "Plate", 4)
    notes = labeled_entry(frame, "Notes", 5)

    def submit() -> None:
        try:
            service_id = int(service_box.get().split(":", 1)[0])
            create_appointment(
                user.user_id,
                service_id,
                motorcycle.get(),
                date.get(),
                time.get(),
                plate.get(),
                notes.get(),
                database_path,
            )
            messagebox.showinfo("Success", "Appointment request submitted.")
        except (ValueError, IndexError) as error:
            show_error(error)

    ttk.Button(frame, text="Book appointment", command=submit).grid(
        row=6, column=0, columnspan=2, pady=12
    )
    return frame