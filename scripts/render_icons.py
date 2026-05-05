#!/usr/bin/env python3
"""
Pocket URO Beacon icon generator (Pillow-only, no external deps).

Generates iOS app icon PNGs from geometric primitives matching the Claude Design
handoff spec (icons/icons.jsx). Uses the "no wordmark" variant for all sizes —
clean beacon-on-navy that scales reliably without font dependencies.

Spec source: ~/Downloads/design_handoff_pocket_uro/icons/icons.jsx
viewBox: 200x200 (scaled by output size / 200)
"""
from __future__ import annotations
import math
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

OUT_DIR = Path(__file__).parent.parent / "v4"
SIZES = [20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180, 192, 512, 1024]

# Palette (from icons.jsx INDIGO_PALETTE)
BG1 = (0x1B, 0x2E, 0x7A)   # #1B2E7A
BG2 = (0x0A, 0x16, 0x48)   # #0A1648
BEAM = (0xE8, 0xEE, 0xFF)  # #E8EEFF
BEAM_GLOW = (0x7A, 0x9B, 0xFF)  # #7A9BFF
BEAD = (0xFF, 0xC8, 0x4A)  # #FFC84A

# Geometry (no-wordmark variant: beamTop=50, beamBase=178, beadY=42, beadR=9)
# Beam shape: tapered trapezoid (apex narrow on top, wide base)
# In viewBox 200x200:
#   beam apex top ≈ y=50, beam base ≈ y=178
#   apex width ≈ 4 (x: 98 to 102), base width ≈ 32 (x: 84 to 116)
#   bead at (100, 42), radius 9
# Glow trapezoid is wider with vertical alpha gradient (0.35 base → 0 top)
# Per spec (icons.jsx, no-wordmark variant):
#   solid beam: half-width 16 at base, 2 at apex; y from 50 (apex) to 178 (base)
#   glow:       half-width 38 at base, 4 at apex; y from (beamTop - 10) = 40 to (beamBase + 2) = 180
#   bead:       (100, 42), r=9
G_BEAM_TOP = 50
G_BEAM_BASE = 178
G_BEAD_Y = 42
G_BEAD_R = 9
G_BEAM_APEX_HALFWIDTH = 2
G_BEAM_BASE_HALFWIDTH = 16
G_GLOW_TOP_Y = 40         # beamTop - 10
G_GLOW_BASE_Y = 180       # beamBase + 2
G_GLOW_APEX_HALFWIDTH = 4
G_GLOW_BASE_HALFWIDTH = 38


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def render_radial_bg(size: int) -> Image.Image:
    """Radial gradient: BG1 at bottom-center → BG2 at corners. Per spec:
    radial-gradient(100% 100% at 50% 100%, #1B2E7A 0%, #0A1648 100%)
    """
    img = Image.new("RGB", (size, size), BG2)
    px = img.load()
    cx = size / 2
    cy = size  # bottom
    # Max distance is from corner to center-bottom
    max_d = math.hypot(cx, cy)
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy) / max_d
            d = min(1.0, d)
            px[x, y] = lerp(BG1, BG2, d)
    return img


def draw_polygon_with_alpha(base: Image.Image, polygon: list[tuple[float, float]], color: tuple, alpha: int):
    """Composite a flat-colored polygon at given alpha onto base."""
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.polygon(polygon, fill=color + (alpha,))
    base.alpha_composite(overlay)


def render_beam_glow(base: Image.Image, scale: float):
    """Glow trapezoid with vertical alpha gradient (0.35 at base → 0 at top).
    Drawn by:
      1) drawing the glow polygon at full opacity into a temp RGBA layer
      2) building a vertical alpha gradient mask (0 at top, 0.35*255 at bottom)
      3) multiplying the gradient into the layer's alpha channel
    This produces a smooth gradient — no banding — and is fast (no pixel loops
    on the geometry itself).
    """
    W, H = base.size
    cx = 100 * scale
    top_y = G_GLOW_TOP_Y * scale
    base_y = G_GLOW_BASE_Y * scale
    apex_hw = G_GLOW_APEX_HALFWIDTH * scale
    base_hw = G_GLOW_BASE_HALFWIDTH * scale
    poly = [
        (cx - apex_hw, top_y),
        (cx + apex_hw, top_y),
        (cx + base_hw, base_y),
        (cx - base_hw, base_y),
    ]
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).polygon(poly, fill=BEAM_GLOW + (255,))
    # Build vertical alpha gradient mask using a 1px-wide column then resize.
    col = Image.new("L", (1, H), 0)
    col_px = col.load()
    for y in range(H):
        if y < top_y:
            a = 0
        elif y >= base_y:
            a = round(255 * 0.35)
        else:
            t = (y - top_y) / (base_y - top_y)
            a = round(255 * 0.35 * t)
        col_px[0, y] = a
    grad = col.resize((W, H))
    # Multiply gradient (L) into the layer's alpha channel.
    layer_alpha = layer.split()[3]
    final_alpha = ImageChops.multiply(layer_alpha, grad)
    layer.putalpha(final_alpha)
    base.alpha_composite(layer)


def render_beam(base: Image.Image, scale: float):
    """Solid white beam — narrower trapezoid in the middle."""
    cx = 100 * scale
    top_y = G_BEAM_TOP * scale
    base_y = G_BEAM_BASE * scale
    apex_hw = G_BEAM_APEX_HALFWIDTH * scale
    base_hw = G_BEAM_BASE_HALFWIDTH * scale
    poly = [
        (cx - apex_hw, top_y),
        (cx + apex_hw, top_y),
        (cx + base_hw, base_y),
        (cx - base_hw, base_y),
    ]
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.polygon(poly, fill=BEAM + (255,))
    base.alpha_composite(overlay)


def render_bead(base: Image.Image, scale: float):
    cx = 100 * scale
    cy = G_BEAD_Y * scale
    r = G_BEAD_R * scale
    # Bead overlay (full-opacity yellow disc)
    bead_overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(bead_overlay).ellipse(
        (cx - r, cy - r, cx + r, cy + r), fill=BEAD + (255,)
    )
    base.alpha_composite(bead_overlay)
    # Highlight on a SEPARATE overlay so its alpha composes with the bead
    # via alpha_composite (rather than overwriting the bead pixel).
    # Spec: r=2.45 (relative to bead r=7), offset (-2, -2). Scaled: hr ≈ 0.35*r.
    hr = 2.45 * scale
    hcx = cx - 2 * scale
    hcy = cy - 2 * scale
    hi_overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(hi_overlay).ellipse(
        (hcx - hr, hcy - hr, hcx + hr, hcy + hr),
        fill=(255, 255, 255, 140),
    )
    base.alpha_composite(hi_overlay)


def render_icon(size: int) -> Image.Image:
    """Render the full icon at given size (square)."""
    # Use 2x supersampling then downscale for cleaner edges on small sizes.
    work_size = size * 2 if size <= 256 else size
    bg = render_radial_bg(work_size).convert("RGBA")
    scale = work_size / 200.0
    render_beam_glow(bg, scale)
    render_beam(bg, scale)
    render_bead(bg, scale)
    if work_size != size:
        bg = bg.resize((size, size), Image.LANCZOS)
    return bg.convert("RGB")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output dir: {OUT_DIR}")
    # Generate at 1024 once (highest fidelity), then resize for smaller sizes
    # for performance. The 1024 image already supersamples (we do explicit
    # 2x supersample inside render_icon), so resampling down is high quality.
    master = render_icon(1024)
    master.save(OUT_DIR / "icon-1024.png", optimize=True)
    print(f"  wrote icon-1024.png  ({master.size[0]}x{master.size[1]})")

    for s in SIZES:
        if s == 1024:
            continue
        out = master.resize((s, s), Image.LANCZOS)
        out_path = OUT_DIR / f"icon-{s}.png"
        out.save(out_path, optimize=True)
        print(f"  wrote icon-{s}.png  ({s}x{s})")

    # apple-touch-icon = 180×180
    shutil.copy(OUT_DIR / "icon-180.png", OUT_DIR / "apple-touch-icon.png")
    print(f"  wrote apple-touch-icon.png (copy of 180)")
    print(f"\nDone. {len(SIZES)} sizes + apple-touch-icon written to {OUT_DIR}")


if __name__ == "__main__":
    main()
