"""Customer dashboard — CustomTkinter with sidebar navigation."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import customtkinter as ctk
from tkinter import ttk
from PIL import Image

from controllers.appointment_controller import list_user_appointments
from controllers.service_controller import list_categories, list_services
from models.service import Service
from models.user import User
from views import theme as T
from views.customer.appointment_form import build_appointment_form
from views.customer.profile import build_profile_view
from views.image_utils import create_placeholder_image, load_ctk_image

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _load_logo(height: int = 60) -> ctk.CTkImage | None:
    """Load the full FGP logo (not the small one)."""
    for name in ("fgp-logo.png", "fgp-logo-small.png"):
        path = _PROJECT_ROOT / name
        if path.exists():
            try:
                img = Image.open(path)
                w, h = img.size
                scale = height / h
                return ctk.CTkImage(img, size=(int(w * scale), height))
            except Exception:
                pass
    return None


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
        rowheight=36,
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
    )
    style.map(
        "FGP.Treeview",
        background=[("selected", T.SURFACE2)],
        foreground=[("selected", T.ACCENT)],
    )


def _nav_btn(sidebar: ctk.CTkFrame, text: str, command) -> ctk.CTkButton:
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


def _build_services_page(
    parent: ctk.CTkFrame,
    database_path: str | None,
    on_book: Callable[[int], None] | None = None,
) -> None:
    """Display available services with a 2-level hierarchy and search: Category Showcase -> Services -> Book."""
    container = ctk.CTkFrame(parent, fg_color=T.BG, corner_radius=0)
    container.pack(fill="both", expand=True)

    current_cat_id: list[int | None] = [None]
    search_query = [""]

    def _render() -> None:
        for w in container.winfo_children():
            w.destroy()

        scroll = ctk.CTkScrollableFrame(container, fg_color=T.BG, corner_radius=0)
        scroll.pack(fill="both", expand=True)

        categories = list_categories(active_only=True, database_path=database_path)
        all_services = list_services(available_only=True, database_path=database_path)

        if not categories:
            ctk.CTkLabel(
                scroll,
                text="No service categories available at this time.",
                font=T.FONT_BODY,
                text_color=T.TEXT_DIM,
            ).pack(pady=60)
            return

        
        search_bar = ctk.CTkFrame(scroll, fg_color="transparent")
        search_bar.pack(fill="x", padx=24, pady=(16, 12))

        search_e = T.entry(search_bar, placeholder="Search services (e.g. cleaning, helmet, repair)...", width=360)
        search_e.pack(side="left", padx=(0, 10))
        if search_query[0]:
            search_e.insert(0, search_query[0])

        def _do_search() -> None:
            search_query[0] = search_e.get().strip()
            _render()

        def _clear_search() -> None:
            search_query[0] = ""
            search_e.delete(0, "end")
            _render()

        T.primary_button(search_bar, "SEARCH", command=_do_search, width=100).pack(side="left", padx=(0, 8))
        if search_query[0]:
            T.ghost_button(search_bar, "CLEAR", command=_clear_search, width=90).pack(side="left")

        search_e.bind("<Return>", lambda _e: _do_search())

        
        if search_query[0]:
            q = search_query[0].lower()
            matched = [
                s for s in all_services
                if q in s.service_name.lower() or q in (s.description or "").lower()
            ]
            ctk.CTkLabel(
                scroll,
                text=f"Search Results for '{search_query[0]}' ({len(matched)} found)",
                font=T.FONT_H2,
                text_color=T.TEXT,
                anchor="w",
            ).pack(anchor="w", padx=24, pady=(8, 12))

            if not matched:
                ctk.CTkLabel(
                    scroll,
                    text="No services found matching your search. Try another keyword.",
                    font=T.FONT_BODY,
                    text_color=T.TEXT_DIM,
                ).pack(pady=40)
            else:
                cat_map = {c.category_id: c.category_name for c in categories}
                for svc in matched:
                    card = T.card(scroll, corner_radius=4)
                    card.pack(fill="x", padx=24, pady=8)

                    row = ctk.CTkFrame(card, fg_color="transparent")
                    row.pack(padx=20, pady=16, fill="x")

                    simg = load_ctk_image(svc.image_path, size=(90, 90), corner_radius=4)
                    if not simg:
                        simg = create_placeholder_image(svc.service_name[:4], size=(90, 90))
                    ctk.CTkLabel(row, image=simg, text="").pack(side="left", padx=(0, 20))

                    info = ctk.CTkFrame(row, fg_color="transparent")
                    info.pack(side="left", fill="x", expand=True)

                    c_name = cat_map.get(svc.category_id, "General")
                    ctk.CTkLabel(
                        info,
                        text=f"{c_name.upper()} · {svc.duration_minutes} MIN",
                        font=T.FONT_SMALL,
                        text_color=T.MUTED,
                        anchor="w",
                    ).pack(anchor="w")

                    ctk.CTkLabel(
                        info,
                        text=svc.service_name,
                        font=T.FONT_H2,
                        text_color=T.TEXT,
                        anchor="w",
                    ).pack(anchor="w", pady=(2, 0))

                    if svc.description:
                        ctk.CTkLabel(
                            info,
                            text=svc.description,
                            font=T.FONT_SMALL,
                            text_color=T.TEXT_DIM,
                            anchor="w",
                            wraplength=480,
                        ).pack(anchor="w", pady=(3, 0))

                    action_box = ctk.CTkFrame(row, fg_color="transparent")
                    action_box.pack(side="right", padx=(16, 0))
                    ctk.CTkLabel(
                        action_box,
                        text=f"₱{svc.price:.2f}",
                        font=T.FONT_H1,
                        text_color=T.ACCENT,
                        anchor="e",
                    ).pack(anchor="e", pady=(0, 8))

                    def _book_m(sid=svc.service_id) -> None:
                        if on_book:
                            on_book(sid)

                    T.primary_button(
                        action_box,
                        "BOOK SERVICE →",
                        command=_book_m,
                        width=160,
                    ).pack(anchor="e")
            return

        
        if current_cat_id[0] is None:
            ctk.CTkLabel(
                scroll,
                text="Select a Category",
                font=T.FONT_H1,
                text_color=T.TEXT,
                anchor="w",
            ).pack(anchor="w", padx=24, pady=(10, 4))
            ctk.CTkLabel(
                scroll,
                text="Choose a gear specialty below to view available maintenance & customization services.",
                font=T.FONT_SMALL,
                text_color=T.MUTED,
                anchor="w",
            ).pack(anchor="w", padx=24, pady=(0, 16))

            for cat in categories:
                cat_services = [s for s in all_services if s.category_id == cat.category_id]
                card = T.card(scroll, corner_radius=4)
                card.pack(fill="x", padx=24, pady=8)

                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(padx=20, pady=16, fill="x")

                
                cimg = load_ctk_image(cat.image_path, size=(90, 90), corner_radius=4)
                if not cimg:
                    cimg = create_placeholder_image(cat.category_name[:4], size=(90, 90))
                ctk.CTkLabel(row, image=cimg, text="").pack(side="left", padx=(0, 20))

                
                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True)
                ctk.CTkLabel(
                    info,
                    text=cat.category_name,
                    font=T.FONT_H2,
                    text_color=T.TEXT,
                    anchor="w",
                ).pack(anchor="w")
                if cat.description:
                    ctk.CTkLabel(
                        info,
                        text=cat.description,
                        font=T.FONT_SMALL,
                        text_color=T.TEXT_DIM,
                        anchor="w",
                        wraplength=480,
                    ).pack(anchor="w", pady=(3, 0))
                ctk.CTkLabel(
                    info,
                    text=f"{len(cat_services)} service(s) available",
                    font=T.FONT_SMALL,
                    text_color=T.ACCENT,
                    anchor="w",
                ).pack(anchor="w", pady=(6, 0))

                
                btn_box = ctk.CTkFrame(row, fg_color="transparent")
                btn_box.pack(side="right", padx=(16, 0))

                def _open_cat(cid=cat.category_id) -> None:
                    current_cat_id[0] = cid
                    _render()

                T.primary_button(
                    btn_box,
                    "VIEW SERVICES →",
                    command=_open_cat,
                    width=170,
                ).pack()

        
        else:
            cat = next((c for c in categories if c.category_id == current_cat_id[0]), None)
            if not cat:
                current_cat_id[0] = None
                _render()
                return

            cat_services = [s for s in all_services if s.category_id == cat.category_id]

            
            top_bar = ctk.CTkFrame(scroll, fg_color="transparent")
            top_bar.pack(fill="x", padx=24, pady=(16, 8))

            def _go_back() -> None:
                current_cat_id[0] = None
                _render()

            T.ghost_button(
                top_bar,
                "← ALL CATEGORIES",
                command=_go_back,
                width=160,
            ).pack(side="left")

            hdr_card = T.card(scroll, corner_radius=4)
            hdr_card.pack(fill="x", padx=24, pady=(6, 16))
            hdr_inner = ctk.CTkFrame(hdr_card, fg_color="transparent")
            hdr_inner.pack(padx=20, pady=16, fill="x")

            cimg = load_ctk_image(cat.image_path, size=(60, 60), corner_radius=4)
            if not cimg:
                cimg = create_placeholder_image(cat.category_name[:4], size=(60, 60))
            ctk.CTkLabel(hdr_inner, image=cimg, text="").pack(side="left", padx=(0, 16))

            hdr_txt = ctk.CTkFrame(hdr_inner, fg_color="transparent")
            hdr_txt.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(
                hdr_txt,
                text=cat.category_name,
                font=T.FONT_H1,
                text_color=T.TEXT,
                anchor="w",
            ).pack(anchor="w")
            if cat.description:
                ctk.CTkLabel(
                    hdr_txt,
                    text=cat.description,
                    font=T.FONT_SMALL,
                    text_color=T.TEXT_DIM,
                    anchor="w",
                    wraplength=600,
                ).pack(anchor="w", pady=(2, 0))

            if not cat_services:
                ctk.CTkLabel(
                    scroll,
                    text="No services are currently active under this category.",
                    font=T.FONT_BODY,
                    text_color=T.TEXT_DIM,
                ).pack(pady=40)
            else:
                for svc in cat_services:
                    card = T.card(scroll, corner_radius=4)
                    card.pack(fill="x", padx=24, pady=8)

                    row = ctk.CTkFrame(card, fg_color="transparent")
                    row.pack(padx=20, pady=16, fill="x")

                    
                    simg = load_ctk_image(svc.image_path, size=(90, 90), corner_radius=4)
                    if not simg:
                        simg = create_placeholder_image(svc.service_name[:4], size=(90, 90))
                    ctk.CTkLabel(row, image=simg, text="").pack(side="left", padx=(0, 20))

                    
                    info = ctk.CTkFrame(row, fg_color="transparent")
                    info.pack(side="left", fill="x", expand=True)
                    ctk.CTkLabel(
                        info,
                        text=svc.service_name,
                        font=T.FONT_H2,
                        text_color=T.TEXT,
                        anchor="w",
                    ).pack(anchor="w")
                    if svc.description:
                        ctk.CTkLabel(
                            info,
                            text=svc.description,
                            font=T.FONT_SMALL,
                            text_color=T.TEXT_DIM,
                            anchor="w",
                            wraplength=450,
                        ).pack(anchor="w", pady=(3, 0))
                    ctk.CTkLabel(
                        info,
                        text=f"Estimated duration: {svc.duration_minutes} min",
                        font=T.FONT_SMALL,
                        text_color=T.MUTED,
                        anchor="w",
                    ).pack(anchor="w", pady=(4, 0))

                    
                    action_box = ctk.CTkFrame(row, fg_color="transparent")
                    action_box.pack(side="right", padx=(16, 0))
                    ctk.CTkLabel(
                        action_box,
                        text=f"₱{svc.price:.2f}",
                        font=T.FONT_H1,
                        text_color=T.ACCENT,
                        anchor="e",
                    ).pack(anchor="e", pady=(0, 8))

                    def _book(sid=svc.service_id) -> None:
                        if on_book:
                            on_book(sid)

                    T.primary_button(
                        action_box,
                        "BOOK SERVICE →",
                        command=_book,
                        width=160,
                    ).pack(anchor="e")

    _render()


def _build_appointments_page(
    parent: ctk.CTkFrame,
    user: User,
    database_path: str | None,
) -> ttk.Treeview:
    """Display this user's appointments."""
    hdr = ctk.CTkFrame(parent, fg_color="transparent")
    hdr.pack(fill="x", padx=20, pady=(16, 4))
    ctk.CTkLabel(hdr, text="My Appointments", font=T.FONT_H2,
                 text_color=T.TEXT, anchor="w").pack(side="left")

    table_frame = ctk.CTkFrame(parent, fg_color="transparent")
    table_frame.pack(fill="both", expand=True, padx=20, pady=(8, 0))

    table = ttk.Treeview(
        table_frame,
        columns=("date", "time", "service", "model", "price", "status"),
        show="headings",
        style="FGP.Treeview",
    )
    for col, heading, width in (
        ("date",    "Date",        110),
        ("time",    "Time",        80),
        ("service", "Service",     190),
        ("model",   "Motorcycle",  170),
        ("price",   "Price",       100),
        ("status",  "Status",      120),
    ):
        table.heading(col, text=T.spaced(heading.upper()))
        table.column(col, width=width, anchor="w")

    sb = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=sb.set)
    table.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    def _load() -> None:
        try:
            if not table.winfo_exists():
                return
            table.delete(*table.get_children())
            services_cache = {
                s.service_id: s.service_name
                for s in Service.list_all(include_deleted=True, database_path=database_path)
            }
            for appt in list_user_appointments(user.user_id, database_path=database_path):
                s_name = services_cache.get(appt.service_id, f"Service #{appt.service_id}")
                table.insert("", "end", values=(
                    appt.appointment_date,
                    appt.appointment_time,
                    s_name,
                    appt.motorcycle_model,
                    f"₱{appt.price_at_booking:.2f}",
                    appt.status.upper(),
                ))
        except Exception:
            pass

    _load()

    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(fill="x", padx=20, pady=10)
    T.ghost_button(bar, "↺  REFRESH", command=_load, width=140).pack(side="left")

    return table


def create_customer_window(
    user: User, database_path: str | None = None, parent: ctk.CTk | None = None
) -> ctk.CTkToplevel:
    T.apply_theme()
    _style_treeview()

    win = ctk.CTkToplevel(parent) if parent else ctk.CTkToplevel()
    win.title(f"FGP — {user.first_name} {user.last_name}")
    win.geometry("1280x800")
    win.configure(fg_color=T.BG)

    
    win.grid_columnconfigure(1, weight=1)
    win.grid_rowconfigure(0, weight=1)

    
    sidebar = ctk.CTkFrame(win, width=260, fg_color=T.SURFACE,
                           border_width=1, border_color=T.BORDER, corner_radius=0)
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_propagate(False)

    
    logo = T.load_logo(height=50, small=True)
    if logo:
        ctk.CTkLabel(sidebar, image=logo, text="").pack(padx=16, pady=(24, 8))
    else:
        ctk.CTkLabel(sidebar, text=T.spaced("FGP"), font=T.FONT_H1,
                     text_color=T.ACCENT, anchor="w").pack(padx=16, pady=(24, 8))

    T.divider(sidebar, width=220).pack(padx=14, pady=(4, 8))

    
    user_box = ctk.CTkFrame(sidebar, fg_color="transparent")
    user_box.pack(padx=16, pady=(6, 14), fill="x")
    av_img = load_ctk_image(user.profile_image, size=(46, 46), corner_radius=23)
    if not av_img:
        av_img = create_placeholder_image(user.first_name[:1].upper(), size=(46, 46), bg_color=T.SURFACE2, text_color=T.ACCENT)
    ctk.CTkLabel(user_box, image=av_img, text="").pack(side="left", padx=(0, 10))

    user_info = ctk.CTkFrame(user_box, fg_color="transparent")
    user_info.pack(side="left", fill="both", expand=True)
    ctk.CTkLabel(user_info, text="Welcome,", font=T.FONT_SMALL,
                 text_color=T.MUTED, anchor="w").pack(anchor="w")
    ctk.CTkLabel(user_info, text=user.first_name, font=T.FONT_H2,
                 text_color=T.TEXT, anchor="w").pack(anchor="w")

    T.divider(sidebar, width=220).pack(padx=14, pady=(0, 12))

    
    content = ctk.CTkFrame(win, fg_color=T.BG, corner_radius=0)
    content.grid(row=0, column=1, sticky="nsew")
    content.grid_rowconfigure(1, weight=1)
    content.grid_columnconfigure(0, weight=1)

    
    header = ctk.CTkFrame(content, height=64, fg_color=T.SURFACE,
                          border_width=1, border_color=T.BORDER, corner_radius=0)
    header.grid(row=0, column=0, sticky="ew")
    header.grid_propagate(False)
    page_title = ctk.CTkLabel(header, text=T.spaced("SERVICES"),
                               font=T.FONT_H2, text_color=T.TEXT, anchor="w")
    page_title.pack(side="left", padx=24)

    page_frame = ctk.CTkFrame(content, fg_color=T.BG, corner_radius=0)
    page_frame.grid(row=1, column=0, sticky="nsew")
    page_frame.grid_rowconfigure(0, weight=1)
    page_frame.grid_columnconfigure(0, weight=1)

    current_btn: list[ctk.CTkButton] = []
    appt_table_ref: list[ttk.Treeview] = []

    def _show(title: str, builder, btn: ctk.CTkButton) -> None:
        for w in page_frame.winfo_children():
            w.destroy()
        page_title.configure(text=T.spaced(title.upper()))
        if current_btn:
            current_btn[0].configure(text_color=T.TEXT_DIM, fg_color="transparent")
            current_btn.clear()
        btn.configure(text_color=T.ACCENT, fg_color=T.SURFACE2)
        current_btn.append(btn)
        inner = ctk.CTkFrame(page_frame, fg_color=T.BG, corner_radius=0)
        inner.grid(row=0, column=0, sticky="nsew")
        inner.grid_rowconfigure(0, weight=1)
        inner.grid_columnconfigure(0, weight=1)
        builder(inner)

    nav_labels = ["Services", "My Appointments", "Book", "Profile"]
    nav_btns: dict[str, ctk.CTkButton] = {}
    for name in nav_labels:
        btn = _nav_btn(sidebar, name, lambda n=name, b=None: None)
        btn.pack(padx=12, pady=3)
        nav_btns[name] = btn

    def _refresh_appts() -> None:
        if appt_table_ref:
            try:
                t = appt_table_ref[0]
                if t.winfo_exists():
                    t.delete(*t.get_children())
                    services_cache = {
                        s.service_id: s.service_name
                        for s in Service.list_all(include_deleted=True, database_path=database_path)
                    }
                    for appt in list_user_appointments(user.user_id, database_path=database_path):
                        s_name = services_cache.get(appt.service_id, f"Service #{appt.service_id}")
                        t.insert("", "end", values=(
                            appt.appointment_date, appt.appointment_time,
                            s_name,
                            appt.motorcycle_model, f"₱{appt.price_at_booking:.2f}",
                            appt.status.upper(),
                        ))
            except Exception:
                pass

    def _pages(name: str, preselected_svc_id: int | None = None) -> None:
        btn = nav_btns[name]
        if name == "Services":
            def _book_direct(sid: int) -> None:
                _pages("Book", preselected_svc_id=sid)

            _show("Services", lambda f: _build_services_page(f, database_path, on_book=_book_direct), btn)
        elif name == "My Appointments":
            def _b(f: ctk.CTkFrame) -> None:
                appt_table_ref.clear()
                t = _build_appointments_page(f, user, database_path)
                appt_table_ref.append(t)
            _show("My Appointments", _b, btn)
        elif name == "Book":
            _show("Book Appointment",
                  lambda f: build_appointment_form(
                      f, user, database_path, _refresh_appts, initial_service_id=preselected_svc_id
                  ),
                  btn)
        elif name == "Profile":
            _show("Profile",
                  lambda f: build_profile_view(f, user, database_path),
                  btn)

    for name in nav_labels:
        nav_btns[name].configure(command=lambda n=name: _pages(n))

    
    def _logout() -> None:
        try:
            win.destroy()
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
            win.destroy()
        except Exception:
            pass
        if parent:
            try:
                parent.destroy()
            except Exception:
                pass

    win.protocol("WM_DELETE_WINDOW", _on_close)

    _pages("Services")
    return win