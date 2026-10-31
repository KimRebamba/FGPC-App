"""Application entry point.

Run with:
    python main.py
"""

from database.db import initialize_database
from views.theme import apply_theme
from views.login import create_login_window


def main() -> None:
    apply_theme()
    initialize_database()
    create_login_window().mainloop()


if __name__ == "__main__":
    main()
