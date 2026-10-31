"""CustomTkinter login screen — FGP Motorcycle Gear."""

from __future__ import annotations

from pathlib import Path

import customtkinter as ctk
from PIL import Image

from controllers.auth_controller import authenticate_user
from database.db import initialize_database
from views import theme as T

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _logo_image() -> ctk.CTkImage | None:
    """Return a CTkImage of the logo, or None if not found."""
    for name in ("fgp-logo-small.png", "fgp-logo.png"):
        path = _PROJECT_ROOT / name
        if path.exists():
            try:
                img = Image.open(path)
                w, h = img.size
                scale = 96 / h
                return ctk.CTkImage(img, size=(int(w * scale), 96))
            except Exception:
                pass
    return None


def create_login_window(database_path: str | None = None) -> ctk.CTk:
    T.apply_theme()

    try:
        initialize_database(database_path)
    except Exception as exc:
        
        _db_error = str(exc)
    else:
        _db_error = None

    root = T.make_window("FGP — Sign In", "500x680")
    root.resizable(False, False)

    
    outer = ctk.CTkFrame(root, fg_color="transparent")
    outer.place(relx=0.5, rely=0.5, anchor="center")

    
    logo = T.load_logo(height=80, small=False)
    if logo:
        ctk.CTkLabel(outer, image=logo, text="").pack(pady=(0, 20))
    else:
        
        ctk.CTkFrame(outer, height=12, fg_color="transparent").pack()

    
    panel = T.card(outer, width=360, corner_radius=6)
    panel.pack(padx=0)

    inner = ctk.CTkFrame(panel, fg_color="transparent")
    inner.pack(padx=28, pady=28, fill="both", expand=True)

    T.section_label(inner, "Sign in to your account").pack(anchor="w", pady=(0, 16))

    
    T.label(inner, "Email", font=T.FONT_LABEL, color=T.TEXT_DIM).pack(anchor="w")
    email_entry = T.entry(inner, placeholder="you@example.com", width=304)
    email_entry.pack(anchor="w", pady=(2, 10))

    
    T.label(inner, "Password", font=T.FONT_LABEL, color=T.TEXT_DIM).pack(anchor="w")
    pw_entry = T.entry(inner, placeholder="••••••••", show="•", width=304)
    pw_entry.pack(anchor="w", pady=(2, 16))

    
    status_lbl = ctk.CTkLabel(
        inner, text="", font=T.FONT_SMALL,
        text_color=T.ERROR, anchor="w", wraplength=304,
    )
    status_lbl.pack(anchor="w", pady=(0, 8))

    def _set_error(msg: str) -> None:
        status_lbl.configure(text=msg, text_color=T.ERROR)

    def _set_success(msg: str) -> None:
        status_lbl.configure(text=msg, text_color=T.SUCCESS)

    def _clear_status() -> None:
        status_lbl.configure(text="")

    
    if _db_error:
        _set_error(f"DB error: {_db_error}")

    
    def _login() -> None:
        _clear_status()
        email = email_entry.get().strip()
        password = pw_entry.get()

        if not email:
            _set_error("Email is required.")
            return
        if not password:
            _set_error("Password is required.")
            return

        try:
            user = authenticate_user(email, password, database_path)
            if user is None:
                _set_error("Invalid email or password.")
                return
            pw_entry.delete(0, "end")
            _clear_status()
            root.withdraw()
            try:
                if user.role == "admin":
                    from views.admin.dashboard import create_admin_window
                    dashboard = create_admin_window(database_path, user, parent=root)
                else:
                    from views.customer.home import create_customer_window
                    dashboard = create_customer_window(user, database_path, parent=root)
            except Exception as exc:
                root.deiconify()
                _set_error(f"Failed to open dashboard: {exc}")
                return

            def _close_all() -> None:
                try:
                    dashboard.destroy()
                except Exception:
                    pass
                try:
                    root.destroy()
                except Exception:
                    pass

            dashboard.protocol("WM_DELETE_WINDOW", _close_all)

        except Exception as exc:
            _set_error(str(exc))

    root.bind("<Return>", lambda _e: _login())

    T.primary_button(inner, "SIGN IN", command=_login, width=304).pack(pady=(0, 0))

    T.divider(inner, width=304).pack(pady=14)

    
    def _open_registration() -> None:
        _clear_status()
        try:
            root.withdraw()
            from views.register import create_register_window
            reg = create_register_window(database_path, parent=root)

            def _back() -> None:
                try:
                    reg.destroy()
                except Exception:
                    pass
                root.deiconify()

            reg.protocol("WM_DELETE_WINDOW", _back)
        except Exception as exc:
            root.deiconify()
            _set_error(f"Could not open registration: {exc}")

    T.ghost_button(inner, "Create an account", command=_open_registration,
                   width=304).pack()

    return root


def main() -> None:
    create_login_window().mainloop()


if __name__ == "__main__":
    main()