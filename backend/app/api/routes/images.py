from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import Response
from pydantic import BaseModel

from app.services import cartoonize_service, library_service

router = APIRouter(prefix="/images", tags=["images"])

ASSETS_DIR = Path("/app/data/assets")


class CartoonizeUrlRequest(BaseModel):
    url: str
    library_id: str | None = None
    symbol_id: str | None = None


@router.post("/cartoonize/url")
async def cartoonize_from_url(req: CartoonizeUrlRequest, request: Request) -> Response:
    """Fetch an image by URL, cartoonize it, and return the PNG."""
    try:
        png_bytes = cartoonize_service.cartoonize_url(req.url)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Cartoonize failed: {exc}") from exc

    # Optionally persist and update the symbol record
    if req.library_id and req.symbol_id:
        filename = f"cartoon_{hashlib.md5(req.url.encode()).hexdigest()[:8]}.png"
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        (ASSETS_DIR / filename).write_bytes(png_bytes)
        base = str(request.base_url).rstrip("/")
        cartoon_url = f"{base}/assets/{filename}"
        library_service.update_symbol_cartoonized(req.library_id, req.symbol_id, cartoon_url)

    return Response(content=png_bytes, media_type="image/png")


@router.post("/cartoonize/upload")
async def cartoonize_upload(file: UploadFile = File(...)) -> Response:
    """Upload an image, cartoonize it, and return the PNG."""
    content = await file.read()
    try:
        png_bytes = cartoonize_service.cartoonize_bytes(content)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Cartoonize failed: {exc}") from exc
    return Response(content=png_bytes, media_type="image/png")
