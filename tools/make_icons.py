#!/usr/bin/env python3
"""Generate Pocket URO app icons.

Design: 2×2 colored quadrants representing the four modules, with a dark
navy rounded square in the center displaying "URO" in white. Outer corners
rounded to play nicely with iOS/macOS squircle masking.
"""
import os
from PIL import Image, ImageDraw, ImageFont

SIZES = {
    "icon-192.png": 192,
    "icon-512.png": 512,
    "apple-touch-icon.png": 180,
}

MODULE_COLORS = {
    "tl": "#2980b9",  # Patient Education
    "tr": "#27ae60",  # PPu Notes
    "bl": "#e67e22",  # Tips & Guide
    "br": "#8e44ad",  # Textbook
}
CENTER_BG = "#1a1a2e"
TEXT_COLOR = "#ffffff"

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def load_font(px: int) -> ImageFont.ImageFont:
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, px)
            except Exception:
                continue
    return ImageFont.load_default()


def make_icon(size: int) -> Image.Image:
    """Full-bleed opaque square. Four colored quadrants with a dark center
    panel containing the "URO" letter mark. iOS/Android apply their own
    rounded-corner mask at display time, so this icon is square-opaque
    to avoid transparent-corner artifacts on Home Screen.
    """
    img = Image.new("RGB", (size, size), CENTER_BG)
    draw = ImageDraw.Draw(img)
    half = size // 2

    draw.rectangle((0, 0, half, half), fill=MODULE_COLORS["tl"])
    draw.rectangle((half, 0, size, half), fill=MODULE_COLORS["tr"])
    draw.rectangle((0, half, half, size), fill=MODULE_COLORS["bl"])
    draw.rectangle((half, half, size, size), fill=MODULE_COLORS["br"])

    # Center dark rounded panel.
    panel = int(size * 0.62)
    off = (size - panel) // 2
    draw.rounded_rectangle(
        (off, off, off + panel, off + panel),
        radius=int(panel * 0.22),
        fill=CENTER_BG,
    )

    # "URO" letter mark.
    text = "URO"
    font_px = int(size * 0.24)
    font = load_font(font_px)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) // 2 - bbox[0]
    ty = (size - th) // 2 - bbox[1]
    draw.text((tx, ty), text, fill=TEXT_COLOR, font=font)

    return img


def main() -> None:
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    for filename, size in SIZES.items():
        icon = make_icon(size)
        path = os.path.join(out_dir, filename)
        icon.save(path, "PNG", optimize=True)
        print(f"wrote {path} ({size}×{size})")


if __name__ == "__main__":
    main()
