"""
Generate a print-ready PDF of Dobble cards using ReportLab.

Layout: 2 circular cards per A4 page (portrait).
Each card is drawn as a white circle with symbol images placed
according to the GameCard placements (normalised [-1,1] coordinates).
"""

from __future__ import annotations

import hashlib
import io
import os
import tempfile
import urllib.request
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas

from app.models.game import Game, GameCard

# A4 dimensions
PAGE_W, PAGE_H = A4          # points  (595 × 842)
MARGIN = 20 * mm
VERTICAL_GAP = 10 * mm  # extra spacing between the two cards on a page

# Calculate card size to fit two circles per page with a gap between them
AVAILABLE_HEIGHT = PAGE_H - 2 * MARGIN - VERTICAL_GAP
CARD_DIAMETER = AVAILABLE_HEIGHT / 2
CARD_RADIUS = CARD_DIAMETER / 2

# Two cards per page, evenly spaced
CARD_Y_TOP = PAGE_H - MARGIN - CARD_RADIUS
CARD_Y_BOT = MARGIN + CARD_RADIUS
CARD_X = PAGE_W / 2


def _fetch_image_bytes(url: str) -> bytes | None:
    if url.startswith("/assets/"):
        local = Path("/app/data/assets") / url.removeprefix("/assets/")
        if local.exists():
            return local.read_bytes()
        return None
    try:
        with urllib.request.urlopen(url, timeout=6) as resp:
            return resp.read()
    except Exception:
        return None


def _render_size_variation(card_index: int, label: str) -> float:
    seed = hashlib.md5(f"{card_index}:{label}".encode("utf-8")).digest()
    factor = 0.85 + (seed[0] / 255.0) * 0.3
    return factor


def _draw_card(c: Canvas, cx: float, cy: float, card: GameCard) -> None:
    """Draw one circular Dobble card centred at (cx, cy)."""
    # Draw images first (without clipping)
    for placement in card.placements:
        # Convert normalised coords to PDF points
        px = cx + placement.cx * CARD_RADIUS
        py = cy + placement.cy * CARD_RADIUS
        base_sym_r = placement.size * CARD_RADIUS
        render_sym_r = base_sym_r * _render_size_variation(card.index, placement.label)

        img_bytes = _fetch_image_bytes(placement.url)
        if img_bytes:
            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    tmp_file.write(img_bytes)
                    tmp_path = tmp_file.name
                try:
                    c.drawImage(
                        tmp_path,
                        px - render_sym_r,
                        py - render_sym_r,
                        width=render_sym_r * 2,
                        height=render_sym_r * 2,
                    )
                finally:
                    os.unlink(tmp_path)
            except Exception:
                c.setFillColor(colors.black)
                c.setFont("Helvetica", max(6, base_sym_r * 0.8))
                c.drawCentredString(px, py - 3, placement.label[:8])
        else:
            c.setFillColor(colors.black)
            c.setFont("Helvetica", max(6, base_sym_r * 0.8))
            c.drawCentredString(px, py - 3, placement.label[:8])

    # Draw card circle outline on top (thinner line)
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.0)
    c.circle(cx, cy, CARD_RADIUS, fill=0, stroke=1)


def generate_pdf(game: Game) -> bytes:
    """Render all cards to a PDF and return the bytes."""
    buf = io.BytesIO()
    c = Canvas(buf, pagesize=A4)

    card_positions = [CARD_Y_TOP, CARD_Y_BOT]
    slot = 0
    cards_processed = 0

    for card in game.cards:
        cy = card_positions[slot]
        _draw_card(c, CARD_X, cy, card)
        slot += 1
        cards_processed += 1

        if slot == 2:
            c.showPage()
            slot = 0

    if slot > 0:
        c.showPage()  # flush last partial page

    c.save()
    pdf_size = len(buf.getvalue())
    print(f"PDF generated: {cards_processed} cards, {pdf_size} bytes")
    return buf.getvalue()
