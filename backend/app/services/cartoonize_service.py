"""
Stylize an image with a soft pastel / watercolour effect using Pillow only.

Algorithm:
  1. Gentle Gaussian blur  — softens photographic detail
  2. Saturation boost      — vivid, warm pastel palette
  3. Brightness lift       — lightens toward pastel register
  4. Posterize (4-bit)     — ~16 flat colour areas, not the harsh 8 of cartoonize
  5. Soft edge overlay     — very light contours for definition (not comic outlines)

The result reads as a painted illustration rather than a hard-edged cartoon,
which children find warmer and more appealing.
"""

from __future__ import annotations

import io
import urllib.request

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def _fetch_image(url: str) -> Image.Image:
    req = urllib.request.Request(url, headers={"User-Agent": "DobbleGenerator/1.0"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        return Image.open(io.BytesIO(resp.read())).convert("RGBA")


def stylize_bytes(img_bytes: bytes) -> bytes:
    """Apply pastel/watercolour stylization to raw image bytes, return PNG."""
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    return _process(img)


def stylize_url(url: str) -> bytes:
    """Fetch an image by URL, stylize it, and return PNG bytes."""
    img = _fetch_image(url)
    return _process(img)


# Keep legacy aliases so existing routes keep working without changes
cartoonize_bytes = stylize_bytes
cartoonize_url = stylize_url


def _process(img: Image.Image) -> bytes:
    # ── Preserve alpha channel ────────────────────────────────────────────
    alpha = img.split()[3] if img.mode == "RGBA" else None
    rgb = img.convert("RGB")

    # 1. Soft blur — removes noise and sharpens large colour areas
    blurred = rgb.filter(ImageFilter.GaussianBlur(radius=1.8))

    # 2. Saturation boost — richer, more expressive colours
    saturated = ImageEnhance.Color(blurred).enhance(1.5)

    # 3. Brightness lift — towards the pastel / airy register
    bright = ImageEnhance.Brightness(saturated).enhance(1.12)

    # 4. Mild contrast reduction — pastel softness (opposite of cartoonize)
    softened = ImageEnhance.Contrast(bright).enhance(0.88)

    # 5. Posterize with 4 bits = 16 colours — smooth enough for painterly look
    painted = ImageOps.posterize(softened, bits=4)

    # 6. Very light edge definition (optional — cosmetic only)
    grey = blurred.convert("L")
    edges = grey.filter(ImageFilter.FIND_EDGES)
    edges = ImageOps.invert(edges)
    # Keep only very definitive edges (threshold = 235 → most edges discarded)
    edges_bin = edges.point(lambda p: 255 if p > 235 else p)
    edges_soft = edges_bin.filter(ImageFilter.GaussianBlur(radius=0.6))

    # Blend softly: 85 % painted, 15 % edge detail
    result_rgb = Image.blend(painted, edges_soft.convert("RGB"), alpha=0.10)

    # Re-attach original alpha so transparent backgrounds stay clean
    result = result_rgb.convert("RGBA")
    if alpha:
        result.putalpha(alpha)

    out = io.BytesIO()
    result.save(out, format="PNG")
    return out.getvalue()
