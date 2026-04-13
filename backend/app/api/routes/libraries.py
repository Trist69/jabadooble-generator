from __future__ import annotations

import asyncio
import hashlib
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel

from app.core import settings_store
from app.models.library import (
    Library,
    LibraryCreate,
    Symbol,
    SymbolCreate,
)
from app.services import gemini_service, library_service, image_service, xai_service

router = APIRouter(prefix="/libraries", tags=["libraries"])

ASSETS_DIR = Path("/app/data/assets")


# ── Library CRUD ──────────────────────────────────────────────────────────


@router.post("", response_model=Library, status_code=201)
async def create_library(data: LibraryCreate) -> Library:
    return library_service.create_library(data)


@router.get("", response_model=list[Library])
async def list_libraries() -> list[Library]:
    return library_service.list_libraries()


@router.get("/{library_id}", response_model=Library)
async def get_library(library_id: str) -> Library:
    lib = library_service.get_library(library_id)
    if lib is None:
        raise HTTPException(status_code=404, detail="Library not found")
    return lib


@router.delete("/{library_id}", status_code=204)
async def delete_library(library_id: str) -> None:
    if not library_service.delete_library(library_id):
        raise HTTPException(status_code=404, detail="Library not found")


# ── Symbol management ─────────────────────────────────────────────────────


@router.post("/{library_id}/symbols", response_model=Symbol, status_code=201)
async def add_symbol(library_id: str, data: SymbolCreate) -> Symbol:
    sym = library_service.add_symbol(library_id, data)
    if sym is None:
        raise HTTPException(status_code=404, detail="Library not found")
    return sym


@router.delete("/{library_id}/symbols/{symbol_id}", status_code=204)
async def remove_symbol(library_id: str, symbol_id: str) -> None:
    if not library_service.remove_symbol(library_id, symbol_id):
        raise HTTPException(status_code=404, detail="Symbol not found")


@router.post("/{library_id}/symbols/upload", response_model=Symbol, status_code=201)
async def upload_symbol(library_id: str, file: UploadFile = File(...)) -> Symbol:
    content = await file.read()
    url = image_service.save_upload(content, file.filename or "upload.png", ASSETS_DIR)
    label = (file.filename or "upload").rsplit(".", 1)[0]
    sym = library_service.add_symbol(library_id, SymbolCreate(label=label, url=url))
    if sym is None:
        raise HTTPException(status_code=404, detail="Library not found")
    return sym


# ── AI image generation ───────────────────────────────────────────────────


class AiGenerateRequest(BaseModel):
    theme: str
    count: int = 13
    style: str | None = None     # overrides the stored default style if provided


class AiGenerateProgress(BaseModel):
    done: int
    total: int
    library: Library


@router.post("/{library_id}/generate/ai", response_model=AiGenerateProgress)
async def generate_ai_symbols(library_id: str, req: AiGenerateRequest) -> AiGenerateProgress:
    """
    Generate `count` cartoon symbol images via Gemini (Nano Banana 🍌)
    and add them to the library.

    Step 1 — Gemini text: produce `count` distinct subject labels for the theme.
    Step 2 — Gemini image: generate one illustration per subject.
    Step 3 — Persist each PNG to /app/data/assets and add to library.

    Returns the updated library plus progress counts.
    Requires the Gemini API key to be configured in Settings.
    """
    from app.services import gemini_service

    lib = library_service.get_library(library_id)
    if lib is None:
        raise HTTPException(status_code=404, detail="Library not found")

    if req.count < 1 or req.count > 57:
        raise HTTPException(status_code=422, detail="count must be between 1 and 57")

    # Step 1: generate subject labels
    try:
        subjects = gemini_service.generate_subjects(req.theme, req.count)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        error_str = str(exc).lower()
        if 'quota exceeded' in error_str or 'resource_exhausted' in error_str:
            raise HTTPException(
                status_code=429, 
                detail="Gemini API quota exceeded. The free tier allows only 20 text requests per day. "
                       "Please try again tomorrow or upgrade your plan at https://ai.google.dev/gemini-api/docs/rate-limits"
            ) from exc
        else:
            raise HTTPException(status_code=502, detail=f"Gemini text error: {exc}") from exc

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    done = 0
    errors: list[str] = []
    provider = settings_store.get("ai_provider", "gemini") or "gemini"

    for subject in subjects:
        try:
            # Step 2: generate image
            if provider == "xai":
                png_bytes = xai_service.generate_image(subject, style=req.style)
            else:
                png_bytes = gemini_service.generate_image(subject, style=req.style)

            # Step 3: persist
            slug = hashlib.md5(f"{library_id}-{subject}".encode()).hexdigest()[:10]
            filename = f"ai_{slug}.png"
            (ASSETS_DIR / filename).write_bytes(png_bytes)
            url = f"/assets/{filename}"

            library_service.add_symbol(library_id, SymbolCreate(label=subject, url=url))
            done += 1

            # Rate limit: 10 RPM = ~6 seconds between requests
            if done < req.count:  # Don't sleep after last one
                await asyncio.sleep(6.5)
        except Exception as exc:
            errors.append(f"{subject}: {exc}")

    updated = library_service.get_library(library_id)
    if updated is None:
        raise HTTPException(status_code=500, detail="Library disappeared during generation")

    return AiGenerateProgress(done=done, total=req.count, library=updated)
