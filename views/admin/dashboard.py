"""CustomTkinter admin dashboard — FGP Motorcycle Gear Services.
Provides complete CRUD (Create, Read, Update, Delete), Image Uploads, and Reports
for Categories, Services, Appointments, Users, and Reports.
"""

from __future__ import annotations

import datetime
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from controllers.appointment_controller import (
    create_appointment,
    delete_appointment,
    delete_appointments,
    list_appointments,
    update_appointment,
    update_appointment_status,
)
from controllers.auth_controller import (
    admin_create_user,
    admin_update_user,
    delete_user,
    delete_users,
    set_user_active,
)
from controllers.service_controller import (
    create_category,
    create_service,
    delete_categories,
    delete_category,
    delete_service,
    delete_services,
    list_categories,
    list_services,
    set_category_active,
    set_service_available,
    update_category,
    update_service,
)
from models.category import Category
from models.service import Service
from models.user import User
from views import theme as T
from views.admin.profile import build_profile_view
from views.image_utils import (
    create_placeholder_image,
    load_ctk_image,
    pick_image_file,
    save_image_to_uploads,
)




def _style_treeview() -> None:
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass
    style.configure(
        "FGP.Treeview",
        background=T.SURFACE,
        foreground=T.TEXT,
        fieldbackground=T.SURFACE,
        rowheight=34,
        font=T.FONT_BODY,
        bordercolor=T.BORDER,
        relief="flat",
    )
    style.configure(
        "FGP.Treeview.Heading",
        background=T.BG,
        foreground=T.MUTED,
        font=T.FONT_SMALL,
        relief="flat",
        bordercolor=T.BORDER,
    )
    style.map(
        "FGP.Treeview",
        background=[("selected", T.SURFACE2)],
        foreground=[("selected", T.ACCENT)],
    )


def _table(parent: ctk.CTkFrame, columns: tuple[str, ...], widths: dict[str, int] | None = None) -> ttk.Treeview:
    table = ttk.Treeview(parent, columns=columns, show="headings", style="FGP.Treeview")
    widths = widths or {}
    for col in columns:
        table.heading(col, text=T.spaced(col.upper()))
        table.column(col, width=widths.get(col, 130), anchor="w")
    sb = ttk.Scrollbar(parent, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=sb.set)
    table.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return table






def _build_categories(parent: ctk.CTkFrame, database_path: str | None) -> None:
    form_card = T.card(parent, corner_radius=4)
    form_card.pack(fill="x", padx=20, pady=(20, 10))

    form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
    form_inner.pack(padx=20, pady=16, fill="x")

    form_title = ctk.CTkLabel(
        form_inner, text=T.spaced("ADD NEW CATEGORY"), font=T.FONT_SMALL, text_color=T.MUTED
    )
    form_title.grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

    
    T.label(form_inner, "Name", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=0, padx=(0, 8), sticky="w"
    )
    name_e = T.entry(form_inner, placeholder="e.g. Helmets", width=180)
    name_e.grid(row=1, column=1, padx=(0, 16), sticky="w")

    T.label(form_inner, "Description", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=2, padx=(0, 8), sticky="w"
    )
    desc_e = T.entry(form_inner, placeholder="Optional details", width=220)
    desc_e.grid(row=1, column=3, padx=(0, 16), sticky="w")

    
    cat_img_path = [None]
    img_preview = ctk.CTkLabel(
        form_inner, text="", image=create_placeholder_image("IMG", size=(50, 50))
    )
    img_preview.grid(row=1, column=4, padx=(0, 10))

    def _choose_img() -> None:
        picked = pick_image_file()
        if picked:
            try:
                rel = save_image_to_uploads(picked, prefix="cat")
                cat_img_path[0] = rel
                cimg = load_ctk_image(rel, size=(50, 50), corner_radius=3)
                if cimg:
                    img_preview.configure(image=cimg)
                status_lbl.configure(text=f"Selected image: {rel}", text_color=T.SUCCESS)
            except Exception as exc:
                status_lbl.configure(text=str(exc), text_color=T.ERROR)

    T.ghost_button(form_inner, "IMAGE", command=_choose_img, width=80).grid(
        row=1, column=5, padx=(0, 16)
    )

    
    status_lbl = ctk.CTkLabel(
        form_inner, text="", font=T.FONT_SMALL, text_color=T.ERROR, anchor="w"
    )
    status_lbl.grid(row=2, column=0, columnspan=6, sticky="w", pady=(8, 0))

    
    btn_box = ctk.CTkFrame(form_inner, fg_color="transparent")
    btn_box.grid(row=3, column=0, columnspan=6, sticky="w", pady=(10, 0))

    editing_cat_id = [None]

    
    search_var = ctk.StringVar()

    table_frame = ctk.CTkFrame(parent, fg_color="transparent")
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
    table = _table(
        table_frame,
        ("id", "name", "description", "active"),
        {"id": 60, "name": 220, "description": 440, "active": 90},
    )

    def _refresh() -> None:
        try:
            if not table.winfo_exists():
                return
            table.delete(*table.get_children())
            q = search_var.get().strip().lower()
            for item in list_categories(database_path=database_path):
                if q and q not in item.category_name.lower() and q not in (item.description or "").lower():
                    continue
                table.insert(
                    "",
                    "end",
                    iid=str(item.category_id),
                    values=(
                        item.category_id,
                        item.category_name,
                        item.description or "-",
                        "Yes" if item.is_active else "No",
                    ),
                )
        except Exception:
            pass

    def _cancel_edit() -> None:
        editing_cat_id[0] = None
        cat_img_path[0] = None
        name_e.delete(0, "end")
        desc_e.delete(0, "end")
        img_preview.configure(image=create_placeholder_image("IMG", size=(50, 50)))
        form_title.configure(text=T.spaced("ADD NEW CATEGORY"))
        add_btn.configure(text=T.spaced("ADD CATEGORY"))
        cancel_btn.pack_forget()
        status_lbl.configure(text="")

    def _save_cat() -> None:
        status_lbl.configure(text="")
        name = name_e.get().strip()
        if not name:
            status_lbl.configure(text="Category name is required.", text_color=T.ERROR)
            return
        try:
            if editing_cat_id[0] is not None:
                update_category(
                    editing_cat_id[0],
                    name,
                    desc_e.get().strip() or None,
                    cat_img_path[0],
                    database_path,
                )
                status_lbl.configure(text=f"Category #{editing_cat_id[0]} updated.", text_color=T.SUCCESS)
                _cancel_edit()
            else:
                create_category(name, desc_e.get().strip() or None, cat_img_path[0], database_path)
                name_e.delete(0, "end")
                desc_e.delete(0, "end")
                cat_img_path[0] = None
                img_preview.configure(image=create_placeholder_image("IMG", size=(50, 50)))
                status_lbl.configure(text="Category added successfully.", text_color=T.SUCCESS)
            _refresh()
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    add_btn = T.primary_button(btn_box, "ADD CATEGORY", command=_save_cat, width=160)
    add_btn.pack(side="left")

    cancel_btn = T.ghost_button(btn_box, "CANCEL", command=_cancel_edit, width=100)

    
    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(fill="x", padx=20, pady=(0, 16))

    def _edit_selected() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Please select a category row to edit.", text_color=T.ERROR)
            return
        cat_id = int(sel[0])
        c = Category.find_by_id(cat_id, database_path)
        if not c:
            status_lbl.configure(text="Category not found.", text_color=T.ERROR)
            return
        editing_cat_id[0] = cat_id
        name_e.delete(0, "end")
        name_e.insert(0, c.category_name)
        desc_e.delete(0, "end")
        desc_e.insert(0, c.description or "")
        cat_img_path[0] = c.image_path
        if c.image_path:
            cimg = load_ctk_image(c.image_path, size=(50, 50), corner_radius=3)
            if cimg:
                img_preview.configure(image=cimg)
        else:
            img_preview.configure(image=create_placeholder_image("IMG", size=(50, 50)))
        form_title.configure(text=T.spaced(f"EDITING CATEGORY #{cat_id}"))
        add_btn.configure(text=T.spaced("SAVE CHANGES"))
        cancel_btn.pack(side="left", padx=10)
        status_lbl.configure(text=f"Loaded category #{cat_id} for editing.", text_color=T.SUCCESS)

    def _toggle() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Select one or more category rows first.", text_color=T.ERROR)
            return
        try:
            for item_id in sel:
                vals = table.item(item_id, "values")
                is_active = vals[3] == "Yes"
                set_category_active(int(vals[0]), not is_active, database_path)
            _refresh()
            status_lbl.configure(
                text=f"Updated status for {len(sel)} category/categories.",
                text_color=T.SUCCESS,
            )
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    def _delete() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Select one or more category rows to delete.", text_color=T.ERROR)
            return
        cat_ids = [int(i) for i in sel]
        try:
            count = delete_categories(cat_ids, database_path)
            if editing_cat_id[0] in cat_ids:
                _cancel_edit()
            _refresh()
            status_lbl.configure(
                text=f"Successfully deleted {count} category/categories (and associated services).",
                text_color=T.SUCCESS,
            )
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    T.primary_button(bar, "EDIT SELECTED", command=_edit_selected, width=150).pack(side="left")
    T.ghost_button(bar, "TOGGLE ACTIVE", command=_toggle, width=150).pack(side="left", padx=8)
    T.danger_button(bar, "DELETE", command=_delete, width=110).pack(side="left", padx=8)
    T.ghost_button(bar, "REFRESH", command=lambda: (_refresh(), status_lbl.configure(text="Categories refreshed.", text_color=T.SUCCESS)), width=110).pack(side="left", padx=8)

    
    search_e = T.entry(bar, placeholder="Search categories...", width=200)
    search_e.pack(side="right")
    search_e.bind("<KeyRelease>", lambda _e: (search_var.set(search_e.get()), _refresh()))

    _refresh()






def _build_services(parent: ctk.CTkFrame, database_path: str | None) -> None:
    form_card = T.card(parent, corner_radius=4)
    form_card.pack(fill="x", padx=20, pady=(20, 10))

    form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
    form_inner.pack(padx=20, pady=16, fill="x")

    form_title = ctk.CTkLabel(
        form_inner, text=T.spaced("ADD NEW SERVICE"), font=T.FONT_SMALL, text_color=T.MUTED
    )
    form_title.grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 10))

    
    cats = list_categories(active_only=False, database_path=database_path)
    cat_names = [f"{c.category_id}: {c.category_name}" for c in cats] or ["1: General"]
    cat_var = ctk.StringVar(value=cat_names[0])

    T.label(form_inner, "Category", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=0, padx=(0, 6), sticky="w"
    )
    cat_box = ctk.CTkComboBox(
        form_inner,
        values=cat_names,
        variable=cat_var,
        width=150,
        height=40,
        fg_color=T.SURFACE2,
        border_color=T.BORDER,
        button_color=T.BORDER,
        text_color=T.TEXT,
        font=T.FONT_BODY,
        state="readonly",
    )
    cat_box.grid(row=1, column=1, padx=(0, 12), sticky="w")

    T.label(form_inner, "Name", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=2, padx=(0, 6), sticky="w"
    )
    name_e = T.entry(form_inner, placeholder="e.g. Brake Check", width=170)
    name_e.grid(row=1, column=3, padx=(0, 12), sticky="w")

    T.label(form_inner, "Price (₱)", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=4, padx=(0, 6), sticky="w"
    )
    price_e = T.entry(form_inner, placeholder="1500.00", width=100)
    price_e.grid(row=1, column=5, padx=(0, 12), sticky="w")

    T.label(form_inner, "Mins", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=6, padx=(0, 6), sticky="w"
    )
    dur_e = T.entry(form_inner, placeholder="30", width=70)
    dur_e.grid(row=1, column=7, sticky="w")

    
    T.label(form_inner, "Description", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=2, column=0, padx=(0, 6), pady=(10, 0), sticky="w"
    )
    desc_e = T.entry(form_inner, placeholder="Details & specs", width=340)
    desc_e.grid(row=2, column=1, columnspan=3, pady=(10, 0), sticky="w")

    svc_img_path = [None]
    img_preview = ctk.CTkLabel(
        form_inner, text="", image=create_placeholder_image("IMG", size=(50, 50))
    )
    img_preview.grid(row=2, column=4, pady=(10, 0), padx=(10, 0))

    def _choose_img() -> None:
        picked = pick_image_file()
        if picked:
            try:
                rel = save_image_to_uploads(picked, prefix="svc")
                svc_img_path[0] = rel
                simg = load_ctk_image(rel, size=(50, 50), corner_radius=3)
                if simg:
                    img_preview.configure(image=simg)
                status_lbl.configure(text=f"Selected image: {rel}", text_color=T.SUCCESS)
            except Exception as exc:
                status_lbl.configure(text=str(exc), text_color=T.ERROR)

    T.ghost_button(form_inner, "CHOOSE PHOTO", command=_choose_img, width=130).grid(
        row=2, column=5, columnspan=2, pady=(10, 0), sticky="w"
    )

    status_lbl = ctk.CTkLabel(
        form_inner, text="", font=T.FONT_SMALL, text_color=T.ERROR, anchor="w"
    )
    status_lbl.grid(row=3, column=0, columnspan=8, sticky="w", pady=(8, 0))

    btn_box = ctk.CTkFrame(form_inner, fg_color="transparent")
    btn_box.grid(row=4, column=0, columnspan=8, sticky="w", pady=(10, 0))

    editing_svc_id = [None]

    
    search_var = ctk.StringVar()

    table_frame = ctk.CTkFrame(parent, fg_color="transparent")
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
    table = _table(
        table_frame,
        ("id", "category", "name", "price", "minutes", "active"),
        {"id": 60, "category": 180, "name": 260, "price": 110, "minutes": 90, "active": 90},
    )

    def _refresh() -> None:
        try:
            if not table.winfo_exists():
                return
            table.delete(*table.get_children())
            
            fresh_cats = list_categories(include_deleted=True, database_path=database_path)
            cat_map = {c.category_id: c.category_name for c in fresh_cats}
            active_cats = [c for c in fresh_cats if not c.is_deleted]
            cat_choices = [f"{c.category_id}: {c.category_name}" for c in active_cats]
            if cat_choices and cat_box.winfo_exists():
                cat_box.configure(values=cat_choices)

            q = search_var.get().strip().lower()
            for item in list_services(database_path=database_path):
                c_name = cat_map.get(item.category_id, f"Category #{item.category_id}")
                if q and q not in item.service_name.lower() and q not in c_name.lower() and q not in (item.description or "").lower():
                    continue
                table.insert(
                    "",
                    "end",
                    iid=str(item.service_id),
                    values=(
                        item.service_id,
                        c_name,
                        item.service_name,
                        f"₱{item.price:.2f}",
                        item.duration_minutes,
                        "Yes" if item.is_available else "No",
                    ),
                )
        except Exception:
            pass

    def _cancel_edit() -> None:
        editing_svc_id[0] = None
        svc_img_path[0] = None
        name_e.delete(0, "end")
        price_e.delete(0, "end")
        dur_e.delete(0, "end")
        desc_e.delete(0, "end")
        img_preview.configure(image=create_placeholder_image("IMG", size=(50, 50)))
        form_title.configure(text=T.spaced("ADD NEW SERVICE"))
        add_btn.configure(text=T.spaced("ADD SERVICE"))
        cancel_btn.pack_forget()
        status_lbl.configure(text="")

    def _save_svc() -> None:
        status_lbl.configure(text="")
        name = name_e.get().strip()
        price_raw = price_e.get().strip()
        dur_raw = dur_e.get().strip()
        if not name or not price_raw or not dur_raw:
            status_lbl.configure(text="Name, price, and duration are required.", text_color=T.ERROR)
            return
        try:
            cid = int(cat_var.get().split(":")[0])
            price = float(price_raw)
            duration = int(dur_raw)
            if editing_svc_id[0] is not None:
                update_service(
                    service_id=editing_svc_id[0],
                    category_id=cid,
                    service_name=name,
                    price=price,
                    duration_minutes=duration,
                    description=desc_e.get().strip() or None,
                    image_path=svc_img_path[0],
                    database_path=database_path,
                )
                status_lbl.configure(text=f"Product #{editing_svc_id[0]} updated.", text_color=T.SUCCESS)
                _cancel_edit()
            else:
                create_service(
                    category_id=cid,
                    service_name=name,
                    price=price,
                    duration_minutes=duration,
                    description=desc_e.get().strip() or None,
                    image_path=svc_img_path[0],
                    database_path=database_path,
                )
                name_e.delete(0, "end")
                price_e.delete(0, "end")
                dur_e.delete(0, "end")
                desc_e.delete(0, "end")
                svc_img_path[0] = None
                img_preview.configure(image=create_placeholder_image("IMG", size=(50, 50)))
                status_lbl.configure(text="Product added successfully.", text_color=T.SUCCESS)
            _refresh()
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    add_btn = T.primary_button(btn_box, "ADD SERVICE", command=_save_svc, width=220)
    add_btn.pack(side="left")

    cancel_btn = T.ghost_button(btn_box, "CANCEL", command=_cancel_edit, width=100)

    
    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(fill="x", padx=20, pady=(0, 16))

    def _edit_selected() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Select a service row to edit.", text_color=T.ERROR)
            return
        svc_id = int(sel[0])
        s = Service.find_by_id(svc_id, database_path)
        if not s:
            status_lbl.configure(text="Service not found.", text_color=T.ERROR)
            return
        editing_svc_id[0] = svc_id
        name_e.delete(0, "end")
        name_e.insert(0, s.service_name)
        price_e.delete(0, "end")
        price_e.insert(0, str(s.price))
        dur_e.delete(0, "end")
        dur_e.insert(0, str(s.duration_minutes))
        desc_e.delete(0, "end")
        desc_e.insert(0, s.description or "")
        svc_img_path[0] = s.image_path
        if s.image_path:
            simg = load_ctk_image(s.image_path, size=(50, 50), corner_radius=3)
            if simg:
                img_preview.configure(image=simg)
        else:
            img_preview.configure(image=create_placeholder_image("IMG", size=(50, 50)))

        
        for val in cat_box.cget("values"):
            if val.startswith(f"{s.category_id}:"):
                cat_var.set(val)
                break

        form_title.configure(text=T.spaced(f"EDITING SERVICE #{svc_id}"))
        add_btn.configure(text=T.spaced("SAVE CHANGES"))
        cancel_btn.pack(side="left", padx=10)
        status_lbl.configure(text=f"Loaded service #{svc_id} for editing.", text_color=T.SUCCESS)

    def _toggle() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Select one or more service rows first.", text_color=T.ERROR)
            return
        try:
            for item_id in sel:
                vals = table.item(item_id, "values")
                is_active = vals[5] == "Yes"
                set_service_available(int(vals[0]), not is_active, database_path)
            _refresh()
            status_lbl.configure(
                text=f"Updated status for {len(sel)} service(s).",
                text_color=T.SUCCESS,
            )
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    def _delete() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Select one or more service rows to delete.", text_color=T.ERROR)
            return
        svc_ids = [int(i) for i in sel]
        try:
            count = delete_services(svc_ids, database_path)
            if editing_svc_id[0] in svc_ids:
                _cancel_edit()
            _refresh()
            status_lbl.configure(
                text=f"Successfully deleted {count} service(s).",
                text_color=T.SUCCESS,
            )
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    T.primary_button(bar, "EDIT SELECTED", command=_edit_selected, width=150).pack(side="left")
    T.ghost_button(bar, "TOGGLE ACTIVE", command=_toggle, width=150).pack(side="left", padx=8)
    T.danger_button(bar, "DELETE", command=_delete, width=110).pack(side="left", padx=8)
    T.ghost_button(bar, "REFRESH", command=lambda: (_refresh(), status_lbl.configure(text="Services refreshed.", text_color=T.SUCCESS)), width=110).pack(side="left", padx=8)

    
    search_e = T.entry(bar, placeholder="Search services...", width=200)
    search_e.pack(side="right")
    search_e.bind("<KeyRelease>", lambda _e: (search_var.set(search_e.get()), _refresh()))

    _refresh()






def _build_appointments(parent: ctk.CTkFrame, database_path: str | None) -> None:
    form_card = T.card(parent, corner_radius=4)
    form_card.pack(fill="x", padx=20, pady=(20, 10))

    form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
    form_inner.pack(padx=20, pady=16, fill="x")

    form_title = ctk.CTkLabel(
        form_inner, text=T.spaced("BOOK / EDIT APPOINTMENT"), font=T.FONT_SMALL, text_color=T.MUTED
    )
    form_title.grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 10))

    users = User.list_all(database_path)
    user_choices = [f"{u.user_id}: {u.first_name} {u.last_name}" for u in users] or ["1: System Admin"]
    user_var = ctk.StringVar(value=user_choices[0])

    T.label(form_inner, "Customer", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=0, padx=(0, 6), sticky="w"
    )
    user_box = ctk.CTkComboBox(
        form_inner, values=user_choices, variable=user_var, width=160, height=40,
        fg_color=T.SURFACE2, border_color=T.BORDER, button_color=T.BORDER, state="readonly"
    )
    user_box.grid(row=1, column=1, padx=(0, 12), sticky="w")

    services = list_services(available_only=False, database_path=database_path)
    svc_choices = [f"{s.service_id}: {s.service_name}" for s in services] or ["1: General Service"]
    svc_var = ctk.StringVar(value=svc_choices[0])

    T.label(form_inner, "Service", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=2, padx=(0, 6), sticky="w"
    )
    svc_box = ctk.CTkComboBox(
        form_inner, values=svc_choices, variable=svc_var, width=180, height=40,
        fg_color=T.SURFACE2, border_color=T.BORDER, button_color=T.BORDER, state="readonly"
    )
    svc_box.grid(row=1, column=3, padx=(0, 12), sticky="w")

    today_str = datetime.date.today().isoformat()
    T.label(form_inner, "Date", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=4, padx=(0, 6), sticky="w"
    )
    date_e = T.entry(form_inner, placeholder="YYYY-MM-DD", width=120)
    date_e.insert(0, today_str)
    date_e.grid(row=1, column=5, padx=(0, 12), sticky="w")

    T.label(form_inner, "Time", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=6, padx=(0, 6), sticky="w"
    )
    time_e = T.entry(form_inner, placeholder="HH:MM", width=90)
    time_e.insert(0, "10:00")
    time_e.grid(row=1, column=7, sticky="w")

    
    T.label(form_inner, "Model", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=2, column=0, padx=(0, 6), pady=(10, 0), sticky="w"
    )
    model_e = T.entry(form_inner, placeholder="e.g. Yamaha R7", width=160)
    model_e.grid(row=2, column=1, pady=(10, 0), padx=(0, 12), sticky="w")

    T.label(form_inner, "Plate", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=2, column=2, padx=(0, 6), pady=(10, 0), sticky="w"
    )
    plate_e = T.entry(form_inner, placeholder="Optional", width=120)
    plate_e.grid(row=2, column=3, pady=(10, 0), padx=(0, 12), sticky="w")

    status_options = ["pending", "confirmed", "completed", "cancelled", "rejected"]
    status_var = ctk.StringVar(value="pending")

    T.label(form_inner, "Status", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=2, column=4, padx=(0, 6), pady=(10, 0), sticky="w"
    )
    status_box = ctk.CTkComboBox(
        form_inner, values=status_options, variable=status_var, width=120, height=40,
        fg_color=T.SURFACE2, border_color=T.BORDER, button_color=T.BORDER, state="readonly"
    )
    status_box.grid(row=2, column=5, pady=(10, 0), sticky="w")

    
    T.label(form_inner, "Notes", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=3, column=0, padx=(0, 6), pady=(8, 0), sticky="nw"
    )
    notes_box = ctk.CTkTextbox(
        form_inner, height=60, fg_color=T.SURFACE2, text_color=T.TEXT,
        border_width=1, border_color=T.BORDER, font=T.FONT_BODY, wrap="word"
    )
    notes_box.grid(row=3, column=1, columnspan=7, sticky="ew", pady=(8, 0))

    status_lbl = ctk.CTkLabel(
        form_inner, text="", font=T.FONT_SMALL, text_color=T.ERROR, anchor="w"
    )
    status_lbl.grid(row=4, column=0, columnspan=8, sticky="w", pady=(8, 0))

    btn_box = ctk.CTkFrame(form_inner, fg_color="transparent")
    btn_box.grid(row=5, column=0, columnspan=8, sticky="w", pady=(10, 0))

    editing_appt_id = [None]
    search_var = ctk.StringVar()

    table_frame = ctk.CTkFrame(parent, fg_color="transparent")
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
    table = _table(
        table_frame,
        ("id", "date", "time", "user", "service", "model", "plate", "price", "status"),
        {"id": 45, "date": 95, "time": 75, "user": 170, "service": 180, "model": 140, "plate": 95, "price": 90, "status": 100},
    )

    def _refresh() -> None:
        try:
            if not table.winfo_exists():
                return
            table.delete(*table.get_children())
            all_u = User.list_all(include_deleted=True, database_path=database_path)
            user_map = {u.user_id: f"{u.first_name} {u.last_name}" for u in all_u}
            all_s = list_services(include_deleted=True, database_path=database_path)
            svc_map = {s.service_id: s.service_name for s in all_s}

            q = search_var.get().strip().lower()
            for item in list_appointments(database_path=database_path):
                u_str = user_map.get(item.user_id, f"User #{item.user_id}")
                s_str = svc_map.get(item.service_id, f"Service #{item.service_id}")
                if q:
                    haystack = f"{item.appointment_date} {item.appointment_time} {u_str} {s_str} {item.motorcycle_model} {item.motorcycle_plate or ''} {item.status} {item.customer_notes or ''}".lower()
                    if q not in haystack:
                        continue
                table.insert(
                    "",
                    "end",
                    iid=str(item.appointment_id),
                    values=(
                        item.appointment_id,
                        item.appointment_date,
                        item.appointment_time,
                        u_str,
                        s_str,
                        item.motorcycle_model,
                        item.motorcycle_plate or "-",
                        f"₱{item.price_at_booking:.2f}",
                        item.status.upper(),
                    ),
                )
        except Exception:
            pass

    def _cancel_edit() -> None:
        editing_appt_id[0] = None
        model_e.delete(0, "end")
        plate_e.delete(0, "end")
        notes_box.delete("1.0", "end")
        status_var.set("pending")
        form_title.configure(text=T.spaced("BOOK / EDIT APPOINTMENT"))
        save_btn.configure(text=T.spaced("BOOK APPOINTMENT"))
        cancel_btn.pack_forget()
        status_lbl.configure(text="")

    def _save_appt() -> None:
        status_lbl.configure(text="")
        model = model_e.get().strip()
        date_val = date_e.get().strip()
        time_val = time_e.get().strip()
        if not model or not date_val or not time_val:
            status_lbl.configure(text="Model, date, and time are required.", text_color=T.ERROR)
            return
        try:
            uid = int(user_var.get().split(":")[0])
            sid = int(svc_var.get().split(":")[0])
            st = status_var.get()
            notes_val = notes_box.get("1.0", "end").strip() or None
            if editing_appt_id[0] is not None:
                update_appointment(
                    appointment_id=editing_appt_id[0],
                    appointment_date=date_val,
                    appointment_time=time_val,
                    motorcycle_model=model,
                    motorcycle_plate=plate_e.get().strip() or None,
                    status=st,
                    customer_notes=notes_val,
                    database_path=database_path,
                )
                status_lbl.configure(text=f"Appointment #{editing_appt_id[0]} updated.", text_color=T.SUCCESS)
                _cancel_edit()
            else:
                create_appointment(
                    user_id=uid,
                    service_id=sid,
                    motorcycle_model=model,
                    appointment_date=date_val,
                    appointment_time=time_val,
                    motorcycle_plate=plate_e.get().strip() or None,
                    customer_notes=notes_val,
                    database_path=database_path,
                )
                model_e.delete(0, "end")
                plate_e.delete(0, "end")
                notes_box.delete("1.0", "end")
                status_lbl.configure(text="Appointment booked successfully.", text_color=T.SUCCESS)
            _refresh()
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    save_btn = T.primary_button(btn_box, "BOOK APPOINTMENT", command=_save_appt, width=180)
    save_btn.pack(side="left")

    cancel_btn = T.ghost_button(btn_box, "CANCEL", command=_cancel_edit, width=100)

    
    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(fill="x", padx=20, pady=(0, 16))

    def _edit_selected() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Select an appointment row to edit.", text_color=T.ERROR)
            return
        from models.appointment import Appointment
        a = Appointment.find_by_id(int(sel[0]), database_path)
        if not a:
            status_lbl.configure(text="Appointment not found.", text_color=T.ERROR)
            return
        editing_appt_id[0] = a.appointment_id
        date_e.delete(0, "end")
        date_e.insert(0, a.appointment_date)
        time_e.delete(0, "end")
        time_e.insert(0, a.appointment_time)
        model_e.delete(0, "end")
        model_e.insert(0, a.motorcycle_model)
        plate_e.delete(0, "end")
        plate_e.insert(0, a.motorcycle_plate or "")
        notes_box.delete("1.0", "end")
        if a.customer_notes:
            notes_box.insert("1.0", a.customer_notes)
        status_var.set(a.status)

        
        for u_val in user_box.cget("values"):
            if u_val.startswith(f"{a.user_id}:"):
                user_var.set(u_val)
                break
        for s_val in svc_box.cget("values"):
            if s_val.startswith(f"{a.service_id}:"):
                svc_var.set(s_val)
                break

        form_title.configure(text=T.spaced(f"EDITING APPOINTMENT #{a.appointment_id}"))
        save_btn.configure(text=T.spaced("SAVE CHANGES"))
        cancel_btn.pack(side="left", padx=10)
        status_lbl.configure(text=f"Loaded appointment #{a.appointment_id} for editing.", text_color=T.SUCCESS)

    def _view_note() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Select an appointment row to view note.", text_color=T.ERROR)
            return
        from models.appointment import Appointment
        a = Appointment.find_by_id(int(sel[0]), database_path)
        if not a:
            status_lbl.configure(text="Appointment not found.", text_color=T.ERROR)
            return
        u = User.find_by_id(a.user_id, database_path)
        u_name = f"{u.first_name} {u.last_name}" if u else f"User #{a.user_id}"

        top = ctk.CTkToplevel(parent.winfo_toplevel())
        top.title(f"Appointment #{a.appointment_id} — Note")
        top.geometry("540x440")
        top.configure(fg_color=T.BG)
        top.grab_set()

        hdr = ctk.CTkFrame(top, fg_color=T.SURFACE, border_width=1, border_color=T.BORDER, corner_radius=0)
        hdr.pack(fill="x", padx=0, pady=0)
        ctk.CTkLabel(hdr, text=T.spaced(f"APPOINTMENT #{a.appointment_id} NOTE"), font=T.FONT_H2, text_color=T.ACCENT).pack(anchor="w", padx=20, pady=(16, 4))
        sub_info = f"Customer: {u_name}  •  Date: {a.appointment_date} {a.appointment_time}  •  Status: {a.status.upper()}"
        ctk.CTkLabel(hdr, text=sub_info, font=T.FONT_SMALL, text_color=T.MUTED).pack(anchor="w", padx=20, pady=(0, 16))

        body = ctk.CTkFrame(top, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=16)

        T.label(body, "Customer Note / Special Instructions:", font=T.FONT_LABEL, color=T.TEXT_DIM).pack(anchor="w", pady=(0, 8))

        note_txt = ctk.CTkTextbox(
            body,
            fg_color=T.SURFACE2,
            text_color=T.TEXT,
            border_width=1,
            border_color=T.BORDER,
            font=T.FONT_BODY,
            wrap="word",
        )
        note_txt.pack(fill="both", expand=True, pady=(0, 14))
        content = a.customer_notes.strip() if a.customer_notes and a.customer_notes.strip() else "(No customer notes attached to this appointment.)"
        note_txt.insert("1.0", content)
        note_txt.configure(state="disabled")

        T.ghost_button(body, "CLOSE", command=top.destroy, width=120).pack(anchor="e")

    def _delete() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Select one or more appointment rows to delete.", text_color=T.ERROR)
            return
        appt_ids = [int(i) for i in sel]
        try:
            count = delete_appointments(appt_ids, database_path)
            if editing_appt_id[0] in appt_ids:
                _cancel_edit()
            _refresh()
            status_lbl.configure(
                text=f"Successfully deleted {count} appointment(s).",
                text_color=T.SUCCESS,
            )
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    T.primary_button(bar, "EDIT SELECTED", command=_edit_selected, width=150).pack(side="left")
    T.ghost_button(bar, "VIEW NOTE", command=_view_note, width=120).pack(side="left", padx=8)
    T.danger_button(bar, "DELETE", command=_delete, width=110).pack(side="left", padx=8)
    T.ghost_button(bar, "REFRESH", command=lambda: (_refresh(), status_lbl.configure(text="Appointments refreshed.", text_color=T.SUCCESS)), width=110).pack(side="left", padx=8)

    
    search_e = T.entry(bar, placeholder="Search appointments...", width=220)
    search_e.pack(side="right")
    search_e.bind("<KeyRelease>", lambda _e: (search_var.set(search_e.get()), _refresh()))

    _refresh()






def _build_users(
    parent: ctk.CTkFrame,
    database_path: str | None,
    current_admin: User | None = None,
) -> None:
    form_card = T.card(parent, corner_radius=4)
    form_card.pack(fill="x", padx=20, pady=(20, 10))

    form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
    form_inner.pack(padx=20, pady=16, fill="x")

    form_title = ctk.CTkLabel(
        form_inner, text=T.spaced("ADD NEW USER"), font=T.FONT_SMALL, text_color=T.MUTED
    )
    form_title.grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 10))

    T.label(form_inner, "First Name", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=0, padx=(0, 6), sticky="w"
    )
    first_e = T.entry(form_inner, placeholder="First", width=130)
    first_e.grid(row=1, column=1, padx=(0, 12), sticky="w")

    T.label(form_inner, "Last Name", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=2, padx=(0, 6), sticky="w"
    )
    last_e = T.entry(form_inner, placeholder="Last", width=130)
    last_e.grid(row=1, column=3, padx=(0, 12), sticky="w")

    T.label(form_inner, "Email", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=1, column=4, padx=(0, 6), sticky="w"
    )
    email_e = T.entry(form_inner, placeholder="user@example.com", width=220)
    email_e.grid(row=1, column=5, padx=(0, 12), sticky="w")

    
    role_var = ctk.StringVar(value="customer")
    T.label(form_inner, "Role", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=2, column=0, padx=(0, 6), pady=(10, 0), sticky="w"
    )
    role_box = ctk.CTkComboBox(
        form_inner, values=["customer", "admin"], variable=role_var, width=130, height=40,
        fg_color=T.SURFACE2, border_color=T.BORDER, button_color=T.BORDER, state="readonly"
    )
    role_box.grid(row=2, column=1, pady=(10, 0), padx=(0, 12), sticky="w")

    T.label(form_inner, "Contact", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=2, column=2, padx=(0, 6), pady=(10, 0), sticky="w"
    )
    contact_e = T.entry(form_inner, placeholder="Phone", width=130)
    contact_e.grid(row=2, column=3, pady=(10, 0), padx=(0, 12), sticky="w")

    T.label(form_inner, "Address", font=T.FONT_LABEL, color=T.TEXT_DIM).grid(
        row=2, column=4, padx=(0, 6), pady=(10, 0), sticky="w"
    )
    addr_e = T.entry(form_inner, placeholder="City, Address", width=180)
    addr_e.grid(row=2, column=5, pady=(10, 0), padx=(0, 12), sticky="w")

    user_img_path = [None]
    img_preview = ctk.CTkLabel(
        form_inner, text="", image=create_placeholder_image("AVATAR", size=(44, 44))
    )
    img_preview.grid(row=2, column=6, pady=(10, 0), padx=(6, 0))

    def _choose_avatar() -> None:
        picked = pick_image_file()
        if picked:
            try:
                rel = save_image_to_uploads(picked, prefix="user")
                user_img_path[0] = rel
                uimg = load_ctk_image(rel, size=(44, 44), corner_radius=22)
                if uimg:
                    img_preview.configure(image=uimg)
                status_lbl.configure(text="Avatar updated.", text_color=T.SUCCESS)
            except Exception as exc:
                status_lbl.configure(text=str(exc), text_color=T.ERROR)

    T.ghost_button(form_inner, "PHOTO", command=_choose_avatar, width=70).grid(
        row=2, column=7, pady=(10, 0), sticky="w"
    )

    status_lbl = ctk.CTkLabel(
        form_inner, text="", font=T.FONT_SMALL, text_color=T.ERROR, anchor="w"
    )
    status_lbl.grid(row=3, column=0, columnspan=8, sticky="w", pady=(8, 0))

    btn_box = ctk.CTkFrame(form_inner, fg_color="transparent")
    btn_box.grid(row=4, column=0, columnspan=8, sticky="w", pady=(10, 0))

    editing_user_id = [None]
    search_var = tk.StringVar(value="")

    table_frame = ctk.CTkFrame(parent, fg_color="transparent")
    table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
    table = _table(
        table_frame,
        ("id", "name", "email", "role", "contact", "active"),
        {"id": 60, "name": 220, "email": 250, "role": 120, "contact": 150, "active": 90},
    )

    def _refresh() -> None:
        try:
            if not table.winfo_exists():
                return
            table.delete(*table.get_children())
            q = search_var.get().strip().lower()
            for u in User.list_all(database_path):
                full_name = f"{u.first_name} {u.last_name}"
                if q:
                    if (
                        q not in str(u.user_id)
                        and q not in full_name.lower()
                        and q not in u.email.lower()
                        and q not in (u.contact_number or "").lower()
                        and q not in u.role.lower()
                    ):
                        continue
                table.insert(
                    "",
                    "end",
                    iid=str(u.user_id),
                    values=(
                        u.user_id,
                        full_name,
                        u.email,
                        u.role.upper(),
                        u.contact_number or "-",
                        "Yes" if u.is_active else "No",
                    ),
                )
        except Exception:
            pass

    def _cancel_edit() -> None:
        editing_user_id[0] = None
        user_img_path[0] = None
        first_e.delete(0, "end")
        last_e.delete(0, "end")
        email_e.delete(0, "end")
        contact_e.delete(0, "end")
        addr_e.delete(0, "end")
        role_var.set("customer")
        img_preview.configure(image=create_placeholder_image("AVATAR", size=(44, 44)))
        form_title.configure(text=T.spaced("ADD NEW USER"))
        save_btn.configure(text=T.spaced("ADD USER"))
        cancel_btn.pack_forget()
        status_lbl.configure(text="")

    def _save_user() -> None:
        status_lbl.configure(text="")
        fname = first_e.get().strip()
        lname = last_e.get().strip()
        email = email_e.get().strip()
        if not fname or not lname or not email:
            status_lbl.configure(text="First name, last name, and email are required.", text_color=T.ERROR)
            return
        try:
            if editing_user_id[0] is not None:
                if current_admin and editing_user_id[0] == current_admin.user_id and role_var.get() != "admin":
                    status_lbl.configure(text="Security: You cannot remove the admin role from your own account.", text_color=T.ERROR)
                    return
                u = User.find_by_id(editing_user_id[0], database_path)
                admin_update_user(
                    user_id=editing_user_id[0],
                    first_name=fname,
                    last_name=lname,
                    email=email,
                    role=role_var.get(),
                    is_active=u.is_active if u else True,
                    address=addr_e.get().strip() or None,
                    contact_number=contact_e.get().strip() or None,
                    profile_image=user_img_path[0],
                    database_path=database_path,
                )
                status_lbl.configure(text=f"User #{editing_user_id[0]} updated.", text_color=T.SUCCESS)
                _cancel_edit()
            else:
                admin_create_user(
                    first_name=fname,
                    last_name=lname,
                    email=email,
                    password="Welcome@123",
                    role=role_var.get(),
                    address=addr_e.get().strip() or None,
                    contact_number=contact_e.get().strip() or None,
                    profile_image=user_img_path[0],
                    database_path=database_path,
                )
                _cancel_edit()
                status_lbl.configure(text="User account created with default password 'Welcome@123'.", text_color=T.SUCCESS)
            _refresh()
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    save_btn = T.primary_button(btn_box, "ADD USER", command=_save_user, width=150)
    save_btn.pack(side="left")

    cancel_btn = T.ghost_button(btn_box, "CANCEL", command=_cancel_edit, width=100)

    
    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(fill="x", padx=20, pady=(0, 16))

    def _edit_selected() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Select a user row to edit.", text_color=T.ERROR)
            return
        u = User.find_by_id(int(sel[0]), database_path)
        if not u:
            status_lbl.configure(text="User not found.", text_color=T.ERROR)
            return
        editing_user_id[0] = u.user_id
        first_e.delete(0, "end")
        first_e.insert(0, u.first_name)
        last_e.delete(0, "end")
        last_e.insert(0, u.last_name)
        email_e.delete(0, "end")
        email_e.insert(0, u.email)
        contact_e.delete(0, "end")
        contact_e.insert(0, u.contact_number or "")
        addr_e.delete(0, "end")
        addr_e.insert(0, u.address or "")
        role_var.set(u.role)
        user_img_path[0] = u.profile_image

        if u.profile_image:
            uimg = load_ctk_image(u.profile_image, size=(44, 44), corner_radius=22)
            if uimg:
                img_preview.configure(image=uimg)
        else:
            img_preview.configure(image=create_placeholder_image(u.first_name[:1], size=(44, 44)))

        form_title.configure(text=T.spaced(f"EDITING USER #{u.user_id}"))
        save_btn.configure(text=T.spaced("SAVE CHANGES"))
        cancel_btn.pack(side="left", padx=10)
        status_lbl.configure(text=f"Loaded user #{u.user_id} for editing.", text_color=T.SUCCESS)

    def _toggle_active() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Select one or more user rows first.", text_color=T.ERROR)
            return
        count = 0
        self_skipped = False
        try:
            for item_id in sel:
                uid = int(item_id)
                if current_admin and uid == current_admin.user_id:
                    self_skipped = True
                    continue
                u = User.find_by_id(uid, database_path)
                if u:
                    set_user_active(uid, not u.is_active, database_path)
                    count += 1
            _refresh()
            if count > 0:
                msg = f"Updated status for {count} user(s)."
                if self_skipped:
                    msg += " (Your own admin account was excluded)"
                status_lbl.configure(text=msg, text_color=T.SUCCESS)
            elif self_skipped:
                status_lbl.configure(
                    text="Security: You cannot deactivate your own admin account.",
                    text_color=T.ERROR,
                )
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    def _delete() -> None:
        status_lbl.configure(text="")
        sel = table.selection()
        if not sel:
            status_lbl.configure(text="Select one or more user rows to delete.", text_color=T.ERROR)
            return
        raw_ids = [int(i) for i in sel]
        self_skipped = False
        target_ids = []
        for uid in raw_ids:
            if current_admin and uid == current_admin.user_id:
                self_skipped = True
            else:
                target_ids.append(uid)

        if not target_ids and self_skipped:
            status_lbl.configure(
                text="Security: You cannot delete your own admin account.",
                text_color=T.ERROR,
            )
            return

        try:
            count = delete_users(target_ids, database_path)
            if editing_user_id[0] in target_ids:
                _cancel_edit()
            _refresh()
            msg = f"Successfully deleted {count} user(s) (and their booking history)."
            if self_skipped:
                msg += " (Your own admin account was excluded)"
            status_lbl.configure(text=msg, text_color=T.SUCCESS)
        except Exception as exc:
            status_lbl.configure(text=str(exc), text_color=T.ERROR)

    T.primary_button(bar, "EDIT SELECTED", command=_edit_selected, width=150).pack(side="left")
    T.ghost_button(bar, "TOGGLE ACTIVE", command=_toggle_active, width=150).pack(side="left", padx=8)
    T.danger_button(bar, "DELETE", command=_delete, width=110).pack(side="left", padx=8)
    T.ghost_button(bar, "REFRESH", command=lambda: (_refresh(), status_lbl.configure(text="Users refreshed.", text_color=T.SUCCESS)), width=110).pack(side="left", padx=8)

    user_search_e = T.entry(bar, placeholder="Search users...", width=200)
    user_search_e.pack(side="right")
    user_search_e.bind("<KeyRelease>", lambda _e: (search_var.set(user_search_e.get()), _refresh()))

    _refresh()






def _build_reports(parent: ctk.CTkFrame, database_path: str | None) -> None:
    scroll = ctk.CTkScrollableFrame(parent, fg_color=T.BG, corner_radius=0)
    scroll.pack(fill="both", expand=True)

    body = ctk.CTkFrame(scroll, fg_color="transparent")
    body.pack(fill="both", expand=True, padx=24, pady=20)

    def _render() -> None:
        try:
            if not body.winfo_exists():
                return
            for w in body.winfo_children():
                w.destroy()

            
            appts = list_appointments(database_path=database_path)
            all_services = list_services(available_only=False, include_deleted=True, database_path=database_path)
            all_categories = list_categories(active_only=False, include_deleted=True, database_path=database_path)
            all_users = User.list_all(include_deleted=True, database_path=database_path)

            completed_appts = [a for a in appts if a.status.lower() == "completed"]
            pending_appts = [a for a in appts if a.status.lower() == "pending"]
            confirmed_appts = [a for a in appts if a.status.lower() == "confirmed"]
            cancelled_appts = [a for a in appts if a.status.lower() == "cancelled"]
            rejected_appts = [a for a in appts if a.status.lower() == "rejected"]

            realized_revenue = sum(a.price_at_booking for a in completed_appts)
            pipeline_revenue = sum(a.price_at_booking for a in (pending_appts + confirmed_appts))

            customers = [u for u in all_users if u.role == "customer" and not u.is_deleted]
            active_customers = [u for u in customers if u.is_active]
            active_services = [s for s in all_services if s.is_available and not s.is_deleted]
            active_categories = [c for c in all_categories if c.is_active and not c.is_deleted]

            
            hdr = ctk.CTkFrame(body, fg_color="transparent")
            hdr.pack(fill="x", pady=(0, 20))

            title_box = ctk.CTkFrame(hdr, fg_color="transparent")
            title_box.pack(side="left")
            ctk.CTkLabel(
                title_box,
                text=T.spaced("REPORTS & ANALYTICS"),
                font=T.FONT_H1,
                text_color=T.TEXT,
                anchor="w",
            ).pack(anchor="w")            

            T.ghost_button(
                hdr,
                "↺  REFRESH METRICS",
                command=_render,
                width=170,
            ).pack(side="right")

            
            kpi_grid = ctk.CTkFrame(body, fg_color="transparent")
            kpi_grid.pack(fill="x", pady=(0, 20))
            for i in range(4):
                kpi_grid.grid_columnconfigure(i, weight=1, uniform="kpi")

            kpi_items = [
                (
                    "TOTAL REVENUE",
                    f"₱{realized_revenue:,.2f}",
                    f"+₱{pipeline_revenue:,.2f} pending pipeline",
                    T.ACCENT,
                ),
                (
                    "APPOINTMENTS",
                    str(len(appts)),
                    f"{len(completed_appts)} completed · {len(pending_appts)} pending",
                    T.TEXT,
                ),
                (
                    "REGISTERED CUSTOMERS",
                    str(len(customers)),
                    f"{len(active_customers)} active account(s)",
                    T.TEXT,
                ),
                (
                    "ACTIVE SERVICES",
                    str(len(active_services)),
                    f"{len(active_categories)} service categories",
                    T.TEXT,
                ),
            ]

            for idx, (label, val, sub, val_color) in enumerate(kpi_items):
                kcard = T.card(kpi_grid, corner_radius=4)
                kcard.grid(row=0, column=idx, padx=(0 if idx == 0 else 8, 0 if idx == 3 else 8), sticky="nsew")
                kpad = ctk.CTkFrame(kcard, fg_color="transparent")
                kpad.pack(padx=18, pady=16, fill="both", expand=True)
                ctk.CTkLabel(
                    kpad,
                    text=T.spaced(label),
                    font=T.FONT_SMALL,
                    text_color=T.MUTED,
                    anchor="w",
                ).pack(anchor="w")
                ctk.CTkLabel(
                    kpad,
                    text=val,
                    font=T.FONT_H1,
                    text_color=val_color,
                    anchor="w",
                ).pack(anchor="w", pady=(6, 2))
                ctk.CTkLabel(
                    kpad,
                    text=sub,
                    font=T.FONT_SMALL,
                    text_color=T.TEXT_DIM,
                    anchor="w",
                ).pack(anchor="w")

            
            mid_grid = ctk.CTkFrame(body, fg_color="transparent")
            mid_grid.pack(fill="x", pady=(0, 20))
            mid_grid.grid_columnconfigure(0, weight=1, uniform="mid")
            mid_grid.grid_columnconfigure(1, weight=1, uniform="mid")

            
            status_card = T.card(mid_grid, corner_radius=4)
            status_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
            status_inner = ctk.CTkFrame(status_card, fg_color="transparent")
            status_inner.pack(padx=20, pady=18, fill="both", expand=True)

            ctk.CTkLabel(
                status_inner,
                text=T.spaced("APPOINTMENT STATUS SUMMARY"),
                font=T.FONT_LABEL,
                text_color=T.MUTED,
                anchor="w",
            ).pack(anchor="w", pady=(0, 12))

            total_count = len(appts) or 1
            status_specs = [
                ("Confirmed", len(confirmed_appts), sum(a.price_at_booking for a in confirmed_appts), T.ACCENT),
                ("Completed", len(completed_appts), sum(a.price_at_booking for a in completed_appts), "#4DFF91"),
                ("Pending", len(pending_appts), sum(a.price_at_booking for a in pending_appts), "#FFD166"),
                ("Cancelled", len(cancelled_appts), sum(a.price_at_booking for a in cancelled_appts), T.MUTED),
                ("Rejected", len(rejected_appts), sum(a.price_at_booking for a in rejected_appts), T.ERROR),
            ]

            for s_name, s_count, s_val, s_color in status_specs:
                s_row = ctk.CTkFrame(status_inner, fg_color="transparent")
                s_row.pack(fill="x", pady=4)
                pct = (s_count / total_count) * 100

                badge = ctk.CTkLabel(
                    s_row,
                    text=f"● {s_name.upper()}",
                    font=T.FONT_SMALL,
                    text_color=s_color,
                    anchor="w",
                    width=110,
                )
                badge.pack(side="left")

                ctk.CTkLabel(
                    s_row,
                    text=f"{s_count} booking(s)",
                    font=T.FONT_BODY,
                    text_color=T.TEXT,
                    anchor="w",
                    width=120,
                ).pack(side="left")

                ctk.CTkLabel(
                    s_row,
                    text=f"{pct:.1f}%",
                    font=T.FONT_SMALL,
                    text_color=T.TEXT_DIM,
                    anchor="w",
                    width=60,
                ).pack(side="left")

                ctk.CTkLabel(
                    s_row,
                    text=f"₱{s_val:,.2f}",
                    font=T.FONT_BODY,
                    text_color=T.ACCENT if s_name in ("Confirmed", "Completed") else T.TEXT_DIM,
                    anchor="e",
                ).pack(side="right")

            
            top_card = T.card(mid_grid, corner_radius=4)
            top_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
            top_inner = ctk.CTkFrame(top_card, fg_color="transparent")
            top_inner.pack(padx=20, pady=18, fill="both", expand=True)

            ctk.CTkLabel(
                top_inner,
                text=T.spaced("SERVICE DEMAND & PRICE"),
                font=T.FONT_LABEL,
                text_color=T.MUTED,
                anchor="w",
            ).pack(anchor="w", pady=(0, 12))

            
            svc_counts: dict[int, tuple[Service, int, float]] = {}
            for s in all_services:
                matched_appts = [a for a in appts if a.service_id == s.service_id]
                vol = sum(a.price_at_booking for a in matched_appts)
                svc_counts[s.service_id] = (s, len(matched_appts), vol)

            ranked = sorted(svc_counts.values(), key=lambda x: (x[1], x[2]), reverse=True)

            if not ranked:
                ctk.CTkLabel(
                    top_inner, text="No service bookings recorded yet.", font=T.FONT_BODY, text_color=T.TEXT_DIM
                ).pack(pady=20)
            else:
                for rank, (svc_obj, b_count, b_vol) in enumerate(ranked[:5], 1):
                    p_row = ctk.CTkFrame(top_inner, fg_color="transparent")
                    p_row.pack(fill="x", pady=4)

                    ctk.CTkLabel(
                        p_row,
                        text=f"#{rank}",
                        font=T.FONT_SMALL,
                        text_color=T.ACCENT if rank == 1 else T.MUTED,
                        width=30,
                        anchor="w",
                    ).pack(side="left")

                    ctk.CTkLabel(
                        p_row,
                        text=svc_obj.service_name,
                        font=T.FONT_BODY,
                        text_color=T.TEXT,
                        anchor="w",
                        width=230,
                    ).pack(side="left")

                    ctk.CTkLabel(
                        p_row,
                        text=f"{b_count} booked",
                        font=T.FONT_SMALL,
                        text_color=T.TEXT_DIM,
                        anchor="w",
                    ).pack(side="left", padx=8)

                    ctk.CTkLabel(
                        p_row,
                        text=f"₱{b_vol:,.2f}",
                        font=T.FONT_BODY,
                        text_color=T.ACCENT,
                        anchor="e",
                    ).pack(side="right")

            
            log_card = T.card(body, corner_radius=4)
            log_card.pack(fill="x", pady=(0, 20))
            log_inner = ctk.CTkFrame(log_card, fg_color="transparent")
            log_inner.pack(padx=20, pady=18, fill="x")

            ctk.CTkLabel(
                log_inner,
                text=T.spaced("RECENT BOOKING ACTIVITY AUDIT"),
                font=T.FONT_LABEL,
                text_color=T.MUTED,
                anchor="w",
            ).pack(anchor="w", pady=(0, 10))

            log_table_frame = ctk.CTkFrame(log_inner, fg_color="transparent")
            log_table_frame.pack(fill="x")
            log_table = _table(
                log_table_frame,
                ("id", "date", "time", "customer", "service", "model", "price", "status"),
                {"id": 50, "date": 100, "time": 70, "customer": 160, "service": 210, "model": 140, "price": 90, "status": 100},
            )

            user_map = {u.user_id: f"{u.first_name} {u.last_name}" for u in all_users}
            svc_map = {s.service_id: s.service_name for s in all_services}

            for item in sorted(appts, key=lambda a: (a.appointment_date, a.appointment_time), reverse=True)[:10]:
                log_table.insert(
                    "",
                    "end",
                    iid=f"rep_{item.appointment_id}",
                    values=(
                        item.appointment_id,
                        item.appointment_date,
                        item.appointment_time,
                        user_map.get(item.user_id, f"User #{item.user_id}"),
                        svc_map.get(item.service_id, f"Service #{item.service_id}"),
                        item.motorcycle_model,
                        f"₱{item.price_at_booking:.2f}",
                        item.status.upper(),
                    ),
                )
        except Exception:
            pass

    _render()




_NAV_ITEMS = ["Categories", "Services", "Appointments", "Users", "Reports", "Profile"]


def _nav_button(sidebar: ctk.CTkFrame, text: str, command) -> ctk.CTkButton:
    return ctk.CTkButton(
        sidebar,
        text=T.spaced(text.upper()),
        command=command,
        width=220,
        height=48,
        anchor="w",
        fg_color="transparent",
        hover_color=T.SURFACE2,
        text_color=T.TEXT_DIM,
        font=T.FONT_BODY,
        corner_radius=3,
    )




def create_admin_window(
    database_path: str | None = None,
    user: User | None = None,
    parent: ctk.CTk | None = None,
) -> ctk.CTk | ctk.CTkToplevel:
    T.apply_theme()
    _style_treeview()

    if parent is not None:
        root = ctk.CTkToplevel(parent)
    elif tk._default_root is not None:
        root = ctk.CTkToplevel()
    else:
        root = ctk.CTk()

    root.title("FGP — Admin Management Dashboard")
    root.geometry("1300x820")
    root.configure(fg_color=T.BG)

    
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)

    
    sidebar = ctk.CTkFrame(
        root, width=260, fg_color=T.SURFACE, border_width=1, border_color=T.BORDER, corner_radius=0
    )
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_propagate(False)

    
    logo = T.load_logo(height=48, small=True)
    if logo:
        ctk.CTkLabel(sidebar, image=logo, text="").pack(padx=16, pady=(24, 8))
    else:
        ctk.CTkLabel(
            sidebar, text=T.spaced("FGP"), font=T.FONT_H1, text_color=T.ACCENT, anchor="w"
        ).pack(padx=16, pady=(24, 8))

    ctk.CTkLabel(
        sidebar, text=T.spaced("ADMIN CONSOLE"), font=T.FONT_SMALL, text_color=T.MUTED, anchor="w"
    ).pack(padx=16, pady=(0, 12))
    T.divider(sidebar, width=220).pack(padx=14, pady=(0, 12))

    
    admin_user = user or (User.list_all(database_path)[0] if User.list_all(database_path) else None)
    if admin_user:
        admin_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        admin_row.pack(padx=16, pady=(4, 14), fill="x")
        av = load_ctk_image(admin_user.profile_image, size=(46, 46), corner_radius=23)
        if not av:
            av = create_placeholder_image(admin_user.first_name[:1].upper(), size=(46, 46), bg_color=T.SURFACE2, text_color=T.ACCENT)
        ctk.CTkLabel(admin_row, image=av, text="").pack(side="left", padx=(0, 10))

        ad_info = ctk.CTkFrame(admin_row, fg_color="transparent")
        ad_info.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(ad_info, text="Admin,", font=T.FONT_SMALL, text_color=T.MUTED, anchor="w").pack(anchor="w")
        ctk.CTkLabel(ad_info, text=admin_user.first_name, font=T.FONT_H2, text_color=T.TEXT, anchor="w").pack(anchor="w")

        T.divider(sidebar, width=220).pack(padx=14, pady=(0, 12))

    
    content = ctk.CTkFrame(root, fg_color=T.BG, corner_radius=0)
    content.grid(row=0, column=1, sticky="nsew", padx=0)
    content.grid_rowconfigure(1, weight=1)
    content.grid_columnconfigure(0, weight=1)

    
    header = ctk.CTkFrame(
        content, height=64, fg_color=T.SURFACE, border_width=1, border_color=T.BORDER, corner_radius=0
    )
    header.grid(row=0, column=0, sticky="ew")
    header.grid_propagate(False)

    page_title = ctk.CTkLabel(
        header, text=T.spaced("CATEGORIES"), font=T.FONT_H2, text_color=T.TEXT, anchor="w"
    )
    page_title.pack(side="left", padx=24, pady=0)

    if admin_user:
        ctk.CTkLabel(
            header,
            text=f"{admin_user.first_name} {admin_user.last_name} ({admin_user.email})",
            font=T.FONT_SMALL,
            text_color=T.MUTED,
        ).pack(side="right", padx=24)

    page_frame = ctk.CTkFrame(content, fg_color=T.BG, corner_radius=0)
    page_frame.grid(row=1, column=0, sticky="nsew")
    page_frame.grid_rowconfigure(0, weight=1)
    page_frame.grid_columnconfigure(0, weight=1)

    current_btn: list[ctk.CTkButton] = []

    def _show(title: str, builder, btn: ctk.CTkButton) -> None:
        for w in page_frame.winfo_children():
            w.destroy()
        page_title.configure(text=T.spaced(title.upper()))
        if current_btn:
            current_btn[0].configure(text_color=T.TEXT_DIM, fg_color="transparent")
            current_btn.clear()
        btn.configure(text_color=T.ACCENT, fg_color=T.SURFACE2)
        current_btn.append(btn)
        frame = ctk.CTkFrame(page_frame, fg_color=T.BG, corner_radius=0)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        builder(frame, database_path)

    builders = {
        "Categories": _build_categories,
        "Services": _build_services,
        "Appointments": _build_appointments,
        "Users": lambda f, db: _build_users(f, db, current_admin=admin_user),
        "Reports": _build_reports,
    }

    nav_btns: dict[str, ctk.CTkButton] = {}
    for name in _NAV_ITEMS:
        if name == "Profile":
            def _profile_builder(frame: ctk.CTkFrame, db: str | None) -> None:
                cur = admin_user or (User.list_all(db)[0] if User.list_all(db) else None)
                if cur:
                    build_profile_view(frame, cur, db)

            btn = _nav_button(sidebar, name, lambda: None)
            btn.pack(padx=14, pady=3)
            nav_btns[name] = btn
            btn.configure(command=lambda n=name, b=btn: _show(n, _profile_builder, b))
        else:
            btn = _nav_button(sidebar, name, lambda: None)
            btn.pack(padx=14, pady=3)
            nav_btns[name] = btn
            btn.configure(command=lambda n=name, b=btn: _show(n, builders[n], b))

    
    def _logout() -> None:
        try:
            root.destroy()
        except Exception:
            pass
        if parent:
            try:
                parent.deiconify()
            except Exception:
                pass

    logout_btn = ctk.CTkButton(
        sidebar,
        text=T.spaced("LOGOUT"),
        command=_logout,
        width=220,
        height=44,
        fg_color="transparent",
        hover_color="#2A0000",
        border_width=1,
        border_color="#441111",
        text_color=T.ERROR,
        font=T.FONT_LABEL,
        corner_radius=3,
    )
    logout_btn.pack(side="bottom", padx=16, pady=20)

    def _on_close() -> None:
        try:
            root.destroy()
        except Exception:
            pass
        if parent:
            try:
                parent.destroy()
            except Exception:
                pass

    root.protocol("WM_DELETE_WINDOW", _on_close)

    
    _show("Categories", _build_categories, nav_btns["Categories"])

    return root


def main() -> None:
    create_admin_window().mainloop()


if __name__ == "__main__":
    main()
