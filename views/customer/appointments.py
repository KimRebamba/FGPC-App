"""Customer appointments view."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from controllers.appointment_controller import (
    cancel_customer_appointment,
    list_user_appointments,
)
from models.user import User


def build_appointments_view(
    parent: tk.Misc, user: User, database_path: str | None = None
) -> ttk.Treeview:
    table = ttk.Treeview(
        parent,
        columns=("id", "date", "time", "status"),
        show="headings",
    )
    for column in ("id", "date", "time", "status"):
        table.heading(column, text=column.title())

    def _refresh() -> None:
        table.delete(*table.get_children())
        for appointment in list_user_appointments(user.user_id, database_path):
            table.insert(
                "",
                "end",
                iid=str(appointment.appointment_id),
                values=(
                    appointment.appointment_id,
                    appointment.appointment_date,
                    appointment.appointment_time,
                    appointment.status.upper(),
                ),
            )

    _refresh()
    table.pack(fill=tk.BOTH, expand=True)
    return table