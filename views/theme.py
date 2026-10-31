"""Design tokens and reusable widget factories for the FGP theme.

Palette
-------
Background  : #0A0A0A  (near-black)
Surface      : #111111  (card/panel)
Border       : #1E1E1E  (hairline)
Muted        : #444444  (disabled / placeholder)
Text         : #FFFFFF  (primary)
Text-dim     : #AAAAAA  (secondary)
Accent       : #C6FF00  (neon-lime — CTAs, prices, active, badge)
"""

from __future__ import annotations

import customtkinter as ctk

from pathlib import Path
from PIL import Image

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


BG       = "#0A0A0A"
SURFACE  = "#111111"
SURFACE2 = "#161616"
BORDER   = "#1E1E1E"
MUTED    = "#555555"
TEXT     = "#FFFFFF"
TEXT_DIM = "#AAAAAA"
ACCENT   = "#C6FF00"
ACCENT_DIM = "#8FB300"
ERROR    = "#FF4D4D"
SUCCESS  = "#4DFF91"


FONT_FAMILY   = "Coolvetica"
FONT_FALLBACK = "Arial"

def _font(size: int, weight: str = "normal") -> tuple[str, int, str]:
    return (FONT_FAMILY, size, weight)




FONT_HERO   = _font(40, "normal")
FONT_H1     = _font(28, "normal")
FONT_H2     = _font(22, "normal")
FONT_BODY   = _font(17, "normal")
FONT_SMALL  = _font(14, "normal")
FONT_LABEL  = _font(15, "normal")
FONT_BTN    = _font(16, "normal")
FONT_INPUT  = _font(16, "normal")
FONT_MONO   = ("Consolas", 15, "normal")



def apply_theme() -> None:
    """Call once at startup to configure CustomTkinter appearance."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")


def load_logo(height: int = 60, small: bool = False) -> ctk.CTkImage | None:
    """Load FGP logo: full logo for login, small logo for customer/admin dashboards."""
    filenames = ("fgp-logo-small.png", "fgp-logo.png") if small else ("fgp-logo.png", "fgp-logo-small.png")
    for name in filenames:
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




def make_window(title: str, size: str = "480x640") -> ctk.CTk:
    root = ctk.CTk()
    root.title(title)
    root.geometry(size)
    root.configure(fg_color=BG)
    root.resizable(True, True)
    return root


def make_toplevel(title: str, size: str = "960x680", parent=None) -> ctk.CTkToplevel:
    win = ctk.CTkToplevel(parent) if parent else ctk.CTkToplevel()
    win.title(title)
    win.geometry(size)
    win.configure(fg_color=BG)
    return win


def card(parent, **kwargs) -> ctk.CTkFrame:
    defaults = dict(fg_color=SURFACE, border_width=1, border_color=BORDER,
                    corner_radius=4)
    return ctk.CTkFrame(parent, **{**defaults, **kwargs})


def label(parent, text: str, font=None, color: str = TEXT,
          anchor: str = "w", **kwargs) -> ctk.CTkLabel:
    return ctk.CTkLabel(parent, text=text, font=font or FONT_BODY,
                        text_color=color, anchor=anchor, **kwargs)


def dim_label(parent, text: str, **kwargs) -> ctk.CTkLabel:
    return label(parent, text, color=TEXT_DIM, font=FONT_SMALL, **kwargs)


def accent_label(parent, text: str, font=None, **kwargs) -> ctk.CTkLabel:
    return label(parent, text, color=ACCENT, font=font or FONT_H2, **kwargs)


def entry(parent, placeholder: str = "", show: str = "",
          width: int = 320, **kwargs) -> ctk.CTkEntry:
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        show=show,
        width=width,
        height=50,
        fg_color=SURFACE2,
        border_color=BORDER,
        border_width=1,
        text_color=TEXT,
        placeholder_text_color=MUTED,
        font=FONT_INPUT,
        corner_radius=3,
        **kwargs,
    )


def primary_button(parent, text: str, command=None,
                   width: int = 320, space_letters: bool = True, **kwargs) -> ctk.CTkButton:
    display_text = spaced(text) if (space_letters and (text.isupper() or " " not in text)) else text
    return ctk.CTkButton(
        parent,
        text=display_text,
        command=command,
        width=width,
        height=50,
        fg_color=ACCENT,
        hover_color=ACCENT_DIM,
        text_color=BG,
        font=FONT_BTN,
        corner_radius=3,
        **kwargs,
    )


def ghost_button(parent, text: str, command=None,
                 width: int = 320, space_letters: bool = True, **kwargs) -> ctk.CTkButton:
    display_text = spaced(text) if (space_letters and (text.isupper() or " " not in text)) else text
    return ctk.CTkButton(
        parent,
        text=display_text,
        command=command,
        width=width,
        height=46,
        fg_color="transparent",
        hover_color=SURFACE2,
        border_width=1,
        border_color=BORDER,
        text_color=TEXT_DIM,
        font=FONT_LABEL,
        corner_radius=3,
        **kwargs,
    )


def danger_button(parent, text: str, command=None,
                  width: int = 160, space_letters: bool = True, **kwargs) -> ctk.CTkButton:
    display_text = spaced(text) if space_letters else text
    return ctk.CTkButton(
        parent,
        text=display_text,
        command=command,
        width=width,
        height=36,
        fg_color="#2A0000",
        hover_color="#550000",
        border_width=1,
        border_color="#FF4D4D",
        text_color=ERROR,
        font=FONT_LABEL,
        corner_radius=3,
        **kwargs,
    )


def divider(parent, **kwargs) -> ctk.CTkFrame:
    return ctk.CTkFrame(parent, height=1, fg_color=BORDER, **kwargs)


def section_label(parent, text: str, space_letters: bool = True) -> ctk.CTkLabel:
    display_text = spaced(text.upper()) if space_letters else text.upper()
    lbl = ctk.CTkLabel(
        parent, text=display_text,
        font=FONT_SMALL,
        text_color=MUTED,
        anchor="w",
    )
    return lbl


def input_row(parent, label_text: str, placeholder: str = "",
              show: str = "", width: int = 320) -> ctk.CTkEntry:
    """Return an entry widget; label is packed above it."""
    lbl = ctk.CTkLabel(parent, text=label_text, font=FONT_LABEL,
                       text_color=TEXT_DIM, anchor="w")
    lbl.pack(anchor="w", pady=(10, 2))
    e = entry(parent, placeholder=placeholder, show=show, width=width)
    e.pack(anchor="w")
    return e


def show_error(message: str | Exception, parent=None) -> None:
    from tkinter import messagebox
    messagebox.showerror("Error", str(message))


def show_info(message: str, title: str = "Success", parent=None) -> None:
    from tkinter import messagebox
    messagebox.showinfo(title, message)


def spaced(text: str, letter_gap: str = " ", word_gap: str = "   ") -> str:
    """Insert `letter_gap` between characters and `word_gap` between words.
    
    Simulates editorial letter-spacing for Coolvetica where it looks too tight:
        spaced("ADMIN PANEL")  →  "A D M I N   P A N E L"
    """
    if not text:
        return text
    
    if "  " in text:
        return text
    words = str(text).split(" ")
    return word_gap.join(letter_gap.join(list(word)) for word in words)
