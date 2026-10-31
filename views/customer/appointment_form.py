"""Customer appointment booking form — CustomTkinter with GUI date/time pickers."""

from __future__ import annotations

import calendar
from collections.abc import Callable
from datetime import date, datetime, timedelta

import customtkinter as ctk

from controllers.appointment_controller import create_appointment
from controllers.service_controller import list_services
from models.user import User
from views import theme as T



_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
_HOURS  = [f"{h:02d}" for h in range(8, 20)]  
_MINUTES = ["00", "15", "30", "45"]  


def _combobox(parent, values: list[str], width: int = 120) -> ctk.CTkComboBox:
    """Themed readonly CTkComboBox."""
    var = ctk.StringVar(value=values[0] if values else "")
    box = ctk.CTkComboBox(
        parent,
        values=values,
        variable=var,
        width=width,
        height=50,
        fg_color=T.SURFACE2,
        border_color=T.BORDER,
        button_color=T.BORDER,
        button_hover_color=T.MUTED,
        dropdown_fg_color=T.SURFACE,
        dropdown_text_color=T.TEXT,
        dropdown_hover_color=T.SURFACE2,
        text_color=T.TEXT,
        font=T.FONT_INPUT,
        corner_radius=3,
        state="readonly",
    )
    return box


def _date_picker(parent) -> tuple[ctk.CTkComboBox, ctk.CTkComboBox, ctk.CTkComboBox]:
    """
    Return (day_box, month_box, year_box).
    Defaults to today. Restricts options to realistic window (today to 30 days ahead).
    """
    today = date.today()
    max_d = today + timedelta(days=30)

    years = [str(today.year)]
    if max_d.year != today.year:
        years.append(str(max_d.year))

    months = _MONTHS[:]

    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(anchor="w", pady=(2, 0))

    month_box = _combobox(row, months, width=160)
    month_box.set(months[today.month - 1])
    month_box.pack(side="left", padx=(0, 8))

    def _days_for(month_name: str, year_str: str) -> list[str]:
        m = _MONTHS.index(month_name) + 1
        try:
            y = int(year_str)
        except ValueError:
            y = today.year
        _, n = calendar.monthrange(y, m)
        return [str(d) for d in range(1, n + 1)]

    day_box = _combobox(row, _days_for(months[today.month - 1], str(today.year)), width=90)
    day_box.set(str(today.day))
    day_box.pack(side="left", padx=(0, 8))

    year_box = _combobox(row, years, width=110)
    year_box.set(str(today.year))
    year_box.pack(side="left")

    def _update_days(*_) -> None:
        try:
            if not day_box.winfo_exists():
                return
            days = _days_for(month_box.get(), year_box.get())
            current = day_box.get()
            day_box.configure(values=days)
            day_box.set(current if current in days else days[-1])
        except Exception:
            pass

    month_box.configure(command=_update_days)
    year_box.configure(command=_update_days)

    return day_box, month_box, year_box


def _time_picker(parent) -> tuple[ctk.CTkComboBox, ctk.CTkComboBox]:
    """Return (hour_box, minute_box). Defaults to next sensible upcoming business hour."""
    now = datetime.now()
    next_h = max(8, min(19, now.hour + 1))
    default_h = f"{next_h:02d}"

    row = ctk.CTkFrame(parent, fg_color="transparent")
    row.pack(anchor="w", pady=(2, 0))

    hour_box = _combobox(row, _HOURS, width=110)
    hour_box.set(default_h)
    hour_box.pack(side="left", padx=(0, 8))

    ctk.CTkLabel(row, text=":", font=T.FONT_H2,
                 text_color=T.TEXT_DIM).pack(side="left", padx=(0, 8))

    minute_box = _combobox(row, _MINUTES, width=100)
    minute_box.set("00")
    minute_box.pack(side="left")

    return hour_box, minute_box




def build_appointment_form(
    parent: ctk.CTkFrame,
    user: User,
    database_path: str | None = None,
    on_saved: Callable[[], None] | None = None,
    initial_service_id: int | None = None,
) -> ctk.CTkFrame:
    scroll = ctk.CTkScrollableFrame(parent, fg_color=T.BG, corner_radius=0)
    scroll.pack(fill="both", expand=True)

    services = list_services(available_only=True, database_path=database_path)

    if not services:
        ctk.CTkLabel(scroll, text="No services are currently available.",
                     font=T.FONT_BODY, text_color=T.TEXT_DIM).pack(pady=60)
        return scroll

    
    service_map = {s.service_name: s.service_id for s in services}
    initial_service = next(
        (s for s in services if s.service_id == initial_service_id),
        services[0],
    )

    
    ctk.CTkLabel(scroll, text="Book an Appointment", font=T.FONT_H2,
                 text_color=T.TEXT, anchor="w").pack(anchor="w", padx=24, pady=(20, 4))
    ctk.CTkLabel(scroll, text="Fill in the details below to request a booking (maximum 30 days in advance).",
                 font=T.FONT_SMALL, text_color=T.MUTED, anchor="w").pack(
        anchor="w", padx=24, pady=(0, 16))

    form_card = T.card(scroll, corner_radius=4)
    form_card.pack(fill="x", padx=20, pady=(0, 20))
    form = ctk.CTkFrame(form_card, fg_color="transparent")
    form.pack(padx=28, pady=24, fill="x")

    def _lbl(text: str) -> None:
        ctk.CTkLabel(form, text=text, font=T.FONT_LABEL,
                     text_color=T.TEXT_DIM, anchor="w").pack(anchor="w", pady=(12, 0))

    
    _lbl("Service")
    service_var = ctk.StringVar(value=initial_service.service_name)
    service_box = ctk.CTkComboBox(
        form,
        values=[s.service_name for s in services],
        variable=service_var,
        width=460,
        height=50,
        fg_color=T.SURFACE2,
        border_color=T.BORDER,
        button_color=T.BORDER,
        button_hover_color=T.MUTED,
        dropdown_fg_color=T.SURFACE,
        dropdown_text_color=T.TEXT,
        dropdown_hover_color=T.SURFACE2,
        text_color=T.TEXT,
        font=T.FONT_BODY,
        corner_radius=3,
        state="readonly",
    )
    service_box.pack(anchor="w", pady=(4, 0))

    
    _lbl("Appointment Date  (Month · Day · Year)")
    day_box, month_box, year_box = _date_picker(form)

    
    _lbl("Preferred Time  (Hour · Minute)")
    hour_box, minute_box = _time_picker(form)

    
    def _text_field(lbl: str, placeholder: str = "") -> ctk.CTkEntry:
        _lbl(lbl)
        e = T.entry(form, placeholder=placeholder, width=460)
        e.pack(anchor="w", pady=(4, 0))
        return e

    moto_e  = _text_field("Motorcycle Model",  "e.g. Honda CB500F")
    plate_e = _text_field("Plate Number",       "e.g. ABC 1234  (optional)")
    notes_e = _text_field("Notes",              "Any special requests?  (optional)")

    
    status_lbl = ctk.CTkLabel(form, text="", font=T.FONT_SMALL,
                               text_color=T.ERROR, anchor="w", wraplength=460)
    status_lbl.pack(anchor="w", pady=(12, 4))

    def _set_error(msg: str) -> None:
        status_lbl.configure(text=msg, text_color=T.ERROR)

    def _set_success(msg: str) -> None:
        status_lbl.configure(text=msg, text_color=T.SUCCESS)

    def _clear_status() -> None:
        status_lbl.configure(text="")

    
    def _save() -> None:
        _clear_status()

        
        try:
            month_idx = _MONTHS.index(month_box.get()) + 1
            picked_date = date(int(year_box.get()), month_idx, int(day_box.get()))
            appt_date = picked_date.isoformat()
        except (ValueError, IndexError) as exc:
            _set_error(f"Invalid date: {exc}")
            return

        today = date.today()
        max_d = today + timedelta(days=30)
        if picked_date < today:
            _set_error("Appointment date cannot be in the past. Please choose a future date.")
            return
        if picked_date > max_d:
            _set_error(f"Appointments can only be booked up to 30 days in advance (until {max_d.isoformat()}).")
            return

        appt_time = f"{hour_box.get()}:{minute_box.get()}"
        if picked_date == today:
            now_t = datetime.now().time()
            picked_t = datetime.strptime(appt_time, "%H:%M").time()
            if picked_t <= now_t:
                _set_error("The selected preferred time has already passed today. Please choose an upcoming time.")
                return

        sid = service_map.get(service_var.get())
        if not sid:
            _set_error("Please select a valid service.")
            return

        if not moto_e.get().strip():
            _set_error("Motorcycle model is required.")
            return

        try:
            create_appointment(
                user_id=user.user_id,
                service_id=sid,
                motorcycle_model=moto_e.get().strip(),
                appointment_date=appt_date,
                appointment_time=appt_time,
                motorcycle_plate=plate_e.get().strip() or None,
                customer_notes=notes_e.get().strip() or None,
                database_path=database_path,
            )
            _set_success("✓ Appointment request submitted successfully!")
            moto_e.delete(0, "end")
            plate_e.delete(0, "end")
            notes_e.delete(0, "end")
            if on_saved:
                try:
                    on_saved()
                except Exception:
                    pass
        except ValueError as exc:
            _set_error(str(exc))
        except Exception as exc:
            _set_error(f"Unexpected error: {exc}")

    book_btn = T.primary_button(form, "BOOK APPOINTMENT", command=_save, width=460)
    book_btn.pack(anchor="w", pady=(0, 4))

    return scroll
