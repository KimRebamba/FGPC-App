"""Customer services view."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from controllers.service_controller import list_services


def build_services_view(
    parent: tk.Misc, database_path: str | None = None
) -> ttk.Treeview:
    table = ttk.Treeview(parent, columns=("service", "price", "duration"), show="headings")
    for column in ("service", "price", "duration"):
        table.heading(column, text=column.title())
    for service in list_services(available_only=True, database_path=database_path):
        table.insert("", "end", values=(service.service_name, service.price, service.duration_minutes))
    table.pack(fill=tk.BOTH, expand=True)
    return table