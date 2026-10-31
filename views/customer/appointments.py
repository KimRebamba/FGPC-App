"""Customer appointments view."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from controllers.appointment_controller import list_user_appointments
from models.user import User


def build_appointments_view(
    parent: tk.Misc, user: User, database_path: str | None = None
) -> ttk.Treeview:
    table = ttk.Treeview(parent, columns=("date", "time", "status"), show="headings")
    for column in ("date", "time", "status"):
        table.heading(column, text=column.title())
    for appointment in list_user_appointments(user.user_id, database_path):
        table.insert(
            "", "end",
            values=(appointment.appointment_date, appointment.appointment_time, appointment.status),
        )
    table.pack(fill=tk.BOTH, expand=True)
    return table