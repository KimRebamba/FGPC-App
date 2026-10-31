"""CustomTkinter registration screen — FGP Motorcycle Gear."""

from __future__ import annotations

import customtkinter as ctk

from controllers.auth_controller import register_user
from database.db import initialize_database
from views import theme as T


def create_register_window(
    database_path: str | None = None,
    parent: ctk.CTk | None = None,
) -> ctk.CTkToplevel:
    """
    Open registration as a Toplevel (never a second CTk root).
    Pass `parent` so it stays tied to the login window's event loop.
    """
    T.apply_theme()

    win = ctk.CTkToplevel(parent)
    win.title("FGP — Create Account")
    win.geometry("540x800")
    win.resizable(False, False)
    win.configure(fg_color=T.BG)

    
    if parent:
        win.transient(parent)
        win.grab_set()

    
    _db_error: str | None = None
    try:
        initialize_database(database_path)
    except Exception as exc:
        _db_error = str(exc)

    
    outer = ctk.CTkFrame(win, fg_color="transparent")
    outer.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(
        outer, text=T.spaced("CREATE YOUR ACCOUNT"),
        font=T.FONT_H1, text_color=T.TEXT, anchor="center",
    ).pack(pady=(0, 20))

    
    panel = T.card(outer, width=480, corner_radius=6)
    panel.pack()

    inner = ctk.CTkFrame(panel, fg_color="transparent")
    inner.pack(padx=32, pady=28, fill="both", expand=True)

    
    def _field(lbl: str, placeholder: str = "", show: str = "") -> ctk.CTkEntry:
        ctk.CTkLabel(inner, text=lbl, font=T.FONT_LABEL,
                     text_color=T.TEXT_DIM, anchor="w").pack(anchor="w")
        e = T.entry(inner, placeholder=placeholder, show=show, width=416)
        e.pack(anchor="w", pady=(2, 10))
        return e

    first_e   = _field("First Name",      "e.g. Kim")
    last_e    = _field("Last Name",        "e.g. Cruz")
    email_e   = _field("Email",            "you@example.com")
    pw_e      = _field("Password",         "Min. 8 characters", show="•")
    contact_e = _field("Contact Number",   "+63 9XX XXX XXXX")
    address_e = _field("Address",          "Street, City")

    
    status_lbl = ctk.CTkLabel(
        inner, text="", font=T.FONT_SMALL,
        text_color=T.ERROR, anchor="w", wraplength=376,
    )
    status_lbl.pack(anchor="w", pady=(2, 8))

    def _set_error(msg: str) -> None:
        status_lbl.configure(text=msg, text_color=T.ERROR)

    def _set_success(msg: str) -> None:
        status_lbl.configure(text=msg, text_color=T.SUCCESS)

    def _clear_status() -> None:
        status_lbl.configure(text="")

    if _db_error:
        _set_error(f"DB error: {_db_error}")

    
    def _register() -> None:
        _clear_status()

        first = first_e.get().strip()
        last  = last_e.get().strip()
        email = email_e.get().strip()
        pw    = pw_e.get()

        
        if not first or not last:
            _set_error("First and last name are required.")
            return
        if not email or "@" not in email:
            _set_error("A valid email address is required.")
            return
        if len(pw) < 8:
            _set_error("Password must be at least 8 characters.")
            return

        try:
            register_user(
                first, last, email, pw,
                address_e.get().strip() or None,
                contact_e.get().strip() or None,
                role="customer",
                database_path=database_path,
            )
            
            _set_success("✓ Account created! Returning to sign in…")

            
            create_btn.configure(state="disabled")

            
            def _auto_return() -> None:
                _close_register()

            win.after(1500, _auto_return)

        except ValueError as exc:
            _set_error(str(exc))
        except Exception as exc:
            _set_error(f"Unexpected error: {exc}")

    def _close_register() -> None:
        try:
            win.grab_release()
            win.destroy()
        except Exception:
            pass
        if parent:
            try:
                parent.deiconify()
            except Exception:
                pass

    win.bind("<Return>", lambda _e: _register())

    create_btn = T.primary_button(
        inner, "CREATE ACCOUNT", command=_register, width=416,
    )
    create_btn.pack(pady=(0, 10))

    back_btn = T.ghost_button(
        inner, "← BACK TO LOGIN", command=_close_register, width=416,
    )
    back_btn.pack()

    return win


def main() -> None:
    root = ctk.CTk()
    root.withdraw()
    win = create_register_window()
    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()