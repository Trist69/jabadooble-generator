"""
Image import adapters.

Sources
───────
hp_api   Harry Potter characters (real photos — apply Pastelify after import)
json     Custom JSON list of {label, url}
upload   Direct file upload

AI generation is handled separately by gemini_service.
"""

from __future__ import annotations

import urllib.request
import json as json_lib
from pathlib import Path

from app.models.library import SymbolCreate

# ── Harry Potter ──────────────────────────────────────────────────────────

HP_API_URL = (
    "https://raw.githubusercontent.com/KostaSav/hp-api/master/data/characters.json"
)


def fetch_hp_characters(limit: int = 20) -> list[SymbolCreate]:
    """Fetch Harry Potter characters from the public HP API JSON file."""
    req = urllib.request.Request(HP_API_URL, headers={"User-Agent": "DobbleGenerator/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        characters: list[dict] = json_lib.loads(resp.read())

    symbols: list[SymbolCreate] = []
    for char in characters[:limit]:
        image = char.get("image", "")
        name = char.get("name", "Unknown")
        if image:
            symbols.append(SymbolCreate(label=name, url=image))
    return symbols


# ── Custom JSON / upload ──────────────────────────────────────────────────

def symbols_from_json(raw: list[dict]) -> list[SymbolCreate]:
    """Parse a list of {label, url} dicts into SymbolCreate objects."""
    result: list[SymbolCreate] = []
    for item in raw:
        label = item.get("label") or item.get("name", "")
        url = item.get("url") or item.get("image", "")
        if label and url:
            result.append(SymbolCreate(label=label, url=url))
    return result


def save_upload(content: bytes, filename: str, assets_dir: Path) -> str:
    """Persist an uploaded image and return its local URL path."""
    assets_dir.mkdir(parents=True, exist_ok=True)
    dest = assets_dir / filename
    dest.write_bytes(content)
    return f"/assets/{filename}"
