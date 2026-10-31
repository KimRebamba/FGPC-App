"""Image loading, saving, thumbnailing, and file-picking utilities."""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageFont
import customtkinter as ctk

PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPLOADS_DIR = PROJECT_ROOT / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


def pick_image_file() -> str | None:
    """Open standard OS file dialog to choose an image file. Return path or None."""
    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.webp *.bmp *.gif"),
            ("All Files", "*.*"),
        ],
    )
    return file_path if file_path else None


def save_image_to_uploads(source_path: str | Path, prefix: str = "img") -> str:
    """
    Copy a chosen image file into the project's uploads/ folder.
    Returns relative path like 'uploads/img_1698765432_name.jpg'.
    """
    src = Path(source_path)
    if not src.exists():
        raise FileNotFoundError(f"Source image file not found: {source_path}")

    
    stem = "".join(c for c in src.stem if c.isalnum() or c in ("-", "_"))[:20]
    filename = f"{prefix}_{int(time.time())}_{stem}{src.suffix.lower()}"
    dest = UPLOADS_DIR / filename
    shutil.copy2(src, dest)
    return f"uploads/{filename}"


def resolve_image_path(image_path: str | Path | None) -> Path | None:
    """Resolve an image path relative to project root or uploads folder."""
    if not image_path:
        return None
    p = Path(image_path)
    if p.is_absolute() and p.exists():
        return p
    
    candidate = PROJECT_ROOT / p
    if candidate.exists():
        return candidate
    
    candidate2 = UPLOADS_DIR / p.name
    if candidate2.exists():
        return candidate2
    return None


def load_ctk_image(
    image_path: str | Path | None,
    size: tuple[int, int] = (120, 120),
    corner_radius: int = 0,
) -> ctk.CTkImage | None:
    """
    Load an image from disk and resize it to size=(width, height).
    Returns ctk.CTkImage, or None if the file cannot be loaded.
    """
    resolved = resolve_image_path(image_path)
    if not resolved:
        return None

    try:
        with Image.open(resolved) as raw:
            
            img = raw.convert("RGBA")
            
            w, h = img.size
            tw, th = size
            scale = max(tw / w, th / h)
            new_w, new_h = int(w * scale), int(h * scale)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            left = (new_w - tw) // 2
            top = (new_h - th) // 2
            img = img.crop((left, top, left + tw, top + th))

            if corner_radius > 0:
                
                mask = Image.new("L", (tw, th), 0)
                draw = ImageDraw.Draw(mask)
                draw.rounded_rectangle([(0, 0), (tw, th)], radius=corner_radius, fill=255)
                rounded = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
                rounded.paste(img, (0, 0), mask)
                img = rounded

            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None


def create_placeholder_image(
    text: str = "NO IMAGE",
    size: tuple[int, int] = (120, 120),
    bg_color: str = "#161616",
    text_color: str = "#555555",
    border_color: str = "#222222",
) -> ctk.CTkImage:
    """Generate a clean dark placeholder image with centered text or icon."""
    tw, th = size
    img = Image.new("RGB", (tw, th), bg_color)
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([(0, 0), (tw - 1, th - 1)], outline=border_color, width=1)

    
    short_text = text[:12].upper()
    try:
        
        bbox = draw.textbbox((0, 0), short_text)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (tw - w) // 2
        y = (th - h) // 2
        draw.text((x, y), short_text, fill=text_color)
    except Exception:
        draw.text((tw // 4, th // 2 - 6), short_text, fill=text_color)

    return ctk.CTkImage(light_image=img, dark_image=img, size=size)
