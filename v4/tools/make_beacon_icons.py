#!/usr/bin/env python3
"""Generate Pocket URO v4 Beacon app icons (Clinical direction).

Design per Claude Design handoff (2026-04-20):
- Deep indigo radial gradient background (#1B2E7A → #0A1648)
- Warm-white beam (tapered trapezoid)
- Golden bead at beam apex with highlight
- Stacked "Pocket" (regular) + "URO" (bold spaced) wordmark
- iOS squircle corner radius (180/1024 of size)
- Small-size fallback: drop wordmark, grow beam
"""
import os
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ---- color tokens (Clinical: INDIGO_PALETTE) ----
BG_TOP    = (27, 46, 122)    # #1B2E7A
BG_BOTTOM = (10, 22, 72)     # #0A1648
BEAM      = (232, 238, 255)  # #E8EEFF
GLOW      = (122, 155, 255)  # #7A9BFF
BEAD      = (255, 200, 74)   # #FFC84A
BEAD_HL   = (255, 255, 255)  # highlight
INK       = (255, 255, 255)  # white wordmark

SIZES = {
    "icon-1024.png": 1024,
    "icon-512.png":   512,
    "icon-192.png":   192,
    "apple-touch-icon.png": 180,
    "icon-120.png":   120,
    "icon-87.png":     87,
    "icon-58.png":     58,
    "icon-40.png":     40,
    "icon-29.png":     29,
}

# Sizes at which we drop the wordmark and grow the beam
WORDMARK_MIN = 87

# Viewport is 200×200 per spec, scaled to target size
VB = 200


def radial_gradient(size):
    """Radial gradient centered near bottom of icon (per spec 'at 50% 100%')."""
    img = Image.new("RGB", (size, size), BG_BOTTOM)
    pixels = img.load()
    cx, cy = size / 2, size  # center at (50%, 100%)
    max_r = math.hypot(size, size)  # corner distance from (50%, 100%)
    for y in range(size):
        for x in range(size):
            r = math.hypot(x - cx, y - cy) / max_r
            # BG_TOP at r=0 (bottom center), BG_BOTTOM at r=1 (far away)
            t = min(1.0, r)
            rr = int(BG_TOP[0] * (1 - t) + BG_BOTTOM[0] * t)
            gg = int(BG_TOP[1] * (1 - t) + BG_BOTTOM[1] * t)
            bb = int(BG_TOP[2] * (1 - t) + BG_BOTTOM[2] * t)
            pixels[x, y] = (rr, gg, bb)
    return img


def squircle_mask(size):
    """iOS-style squircle mask — approximate with rounded square at r=180/1024 of size."""
    r = int(size * 180 / 1024)
    m = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=r, fill=255)
    return m


def vb_to_px(v, size):
    return v / VB * size


def draw_beam_glow(img, size, beam_base_y_vb, beam_top_y_vb):
    """Vertical linear-gradient glow behind the beam."""
    overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx = size / 2
    base_y = vb_to_px(beam_base_y_vb + 2, size)
    top_y  = vb_to_px(beam_top_y_vb - 10, size)
    halo_hw_base = vb_to_px(38, size)
    halo_hw_top  = vb_to_px(4, size)
    # Trapezoid for halo — draw as a series of horizontal strips for gradient
    bands = max(30, int(size / 8))
    for i in range(bands):
        t = i / bands  # 0 at base, 1 at apex
        y = base_y + (top_y - base_y) * t
        next_y = base_y + (top_y - base_y) * (i + 1) / bands
        hw = halo_hw_base + (halo_hw_top - halo_hw_base) * t
        # Opacity: 35% at bottom → 0% at top
        a = int(255 * 0.35 * (1 - t))
        y0, y1 = sorted((y, next_y))
        draw.rectangle(
            (cx - hw, y0, cx + hw, y1),
            fill=(GLOW[0], GLOW[1], GLOW[2], a),
        )
    # Soft blur for halo
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=size / 100))
    img.paste(overlay, (0, 0), overlay)


def draw_beam(img, size, beam_base_y_vb, beam_top_y_vb):
    """Main beam — tapered trapezoid."""
    draw = ImageDraw.Draw(img, "RGBA")
    cx = size / 2
    base_y = vb_to_px(beam_base_y_vb, size)
    top_y  = vb_to_px(beam_top_y_vb, size)
    base_hw = vb_to_px(16, size)
    top_hw  = vb_to_px(2, size)
    # Quadrilateral points (tapered)
    pts = [
        (cx - base_hw, base_y),
        (cx - top_hw,  top_y),
        (cx + top_hw,  top_y),
        (cx + base_hw, base_y),
    ]
    draw.polygon(pts, fill=BEAM + (255,))


def draw_bead(img, size, bead_y_vb, bead_r_vb):
    """Golden bead with white highlight."""
    draw = ImageDraw.Draw(img, "RGBA")
    cx = size / 2
    by = vb_to_px(bead_y_vb, size)
    br = vb_to_px(bead_r_vb, size)
    # main bead
    draw.ellipse((cx - br, by - br, cx + br, by + br), fill=BEAD + (255,))
    # highlight: offset (-2, -2) in 200 viewBox, radius 35% of bead
    hx = cx + vb_to_px(-2, size)
    hy = by + vb_to_px(-2, size)
    hr = br * 0.35
    draw.ellipse((hx - hr, hy - hr, hx + hr, hy + hr),
                 fill=BEAD_HL + (140,))


def find_font(preferred_weight, px):
    """Return an ImageFont, preferring San Francisco family if available."""
    candidates = [
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, int(px))
            except Exception:
                continue
    return ImageFont.load_default()


def draw_wordmark(img, size):
    """Stacked 'Pocket' / 'URO' centered in lower half."""
    draw = ImageDraw.Draw(img, "RGBA")
    cx = size / 2

    # 'Pocket' — SF Pro Display 500, 20pt (at VB=200), centered at y=128
    pocket_px = vb_to_px(22, size)
    font_pocket = find_font("medium", pocket_px)
    pocket_y = vb_to_px(128, size)
    draw.text((cx, pocket_y), "Pocket",
              font=font_pocket, fill=INK + (int(255 * 0.88),),
              anchor="mm")

    # 'URO' — SF Pro Display 800, 40pt at VB=200, letter-spacing +4, centered y=172
    uro_px = vb_to_px(44, size)
    font_uro = find_font("bold", uro_px)
    uro_y = vb_to_px(172, size)
    # Pillow doesn't natively support letter-spacing — draw letter by letter
    letters = ["U", "R", "O"]
    # Measure letter widths first
    widths = []
    for L in letters:
        bbox = draw.textbbox((0, 0), L, font=font_uro)
        widths.append(bbox[2] - bbox[0])
    spacing_extra = vb_to_px(4, size)
    total_w = sum(widths) + spacing_extra * (len(letters) - 1)
    x = cx - total_w / 2
    for L, w in zip(letters, widths):
        draw.text((x, uro_y), L, font=font_uro, fill=INK + (255,), anchor="lm")
        x += w + spacing_extra


def make_icon(size, hide_wordmark=False):
    """Build the icon at a given size."""
    # 1. Radial background
    base = radial_gradient(size).convert("RGBA")

    # 2. Beam glow (behind beam)
    if hide_wordmark:
        beam_top_y = 50
        beam_base_y = 178
        bead_y = 42
        bead_r = 9
    else:
        beam_top_y = 28
        beam_base_y = 90
        bead_y = 22
        bead_r = 7

    draw_beam_glow(base, size, beam_base_y, beam_top_y)
    draw_beam(base, size, beam_base_y, beam_top_y)
    draw_bead(base, size, bead_y, bead_r)

    # 3. Wordmark
    if not hide_wordmark:
        draw_wordmark(base, size)

    # 4. Clip to squircle
    mask = squircle_mask(size)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(base, (0, 0), mask)
    return out


def main():
    for filename, size in SIZES.items():
        hide = size < WORDMARK_MIN
        icon = make_icon(size, hide_wordmark=hide)
        # For the PWA main icons (not @<WORDMARK_MIN>), save as RGB with opaque bg for iOS home screen
        path = os.path.join(OUT_DIR, filename)
        # If squircle mask gave transparent corners, flatten onto black
        flat = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        flat.paste(icon, (0, 0), icon)
        flat.convert("RGBA").save(path, "PNG", optimize=True)
        print(f"wrote {filename:<30}  ({size}×{size}){' [beam only]' if hide else ''}")


if __name__ == "__main__":
    main()
