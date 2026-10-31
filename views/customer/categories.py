"""Customer categories view."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from controllers.service_controller import list_categories


def build_categories_view(
    parent: tk.Misc, database_path: str | None = None
) -> ttk.Treeview:
    table = ttk.Treeview(parent, columns=("category", "description"), show="headings")
    table.heading("category", text="Category")
    table.heading("description", text="Description")
    for category in list_categories(active_only=True, database_path=database_path):
        table.insert("", "end", values=(category.category_name, category.description or ""))
    table.pack(fill=tk.BOTH, expand=True)
    return table