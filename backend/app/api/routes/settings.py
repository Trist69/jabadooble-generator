"""
App settings API — stores configuration in the SQLite settings store.

The API key is write-only from the outside: GET /settings never returns
the raw key value, only whether it is set.  This prevents accidental
exposure in browser devtools or logs.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core import settings_store
from app.services import gemini_service, xai_service

router = APIRouter(prefix="/settings", tags=["settings"])

PROVIDERS = ["gemini", "xai"]


class SettingsResponse(BaseModel):
    gemini_api_key_set: bool
    xai_api_key_set: bool
    ai_provider: str
    gemini_model: str
    xai_model: str
    generation_style: str


class ApiKeyUpdate(BaseModel):
    provider: str = "gemini"
    api_key: str


class ProviderUpdate(BaseModel):
    provider: str


class ModelUpdate(BaseModel):
    provider: str = "gemini"
    model: str


class StyleUpdate(BaseModel):
    style: str


@router.get("", response_model=SettingsResponse)
async def get_settings() -> SettingsResponse:
    return SettingsResponse(
        gemini_api_key_set=bool(settings_store.get("gemini_api_key")),
        xai_api_key_set=bool(settings_store.get("xai_api_key")),
        ai_provider=settings_store.get("ai_provider", "gemini") or "gemini",
        gemini_model=settings_store.get("gemini_model", gemini_service.AVAILABLE_MODELS[0]) or "",
        xai_model=settings_store.get("xai_model", xai_service.AVAILABLE_MODELS[0]) or "",
        generation_style=settings_store.get(
            "generation_style",
            "cute colourful cartoon illustration, children's sticker style, "
            "simple clean design, white background, no text, centred subject",
        ) or "",
    )


@router.put("/api-key", status_code=204)
async def set_api_key(body: ApiKeyUpdate) -> None:
    if body.provider not in PROVIDERS:
        raise HTTPException(status_code=422, detail=f"Unknown provider: {body.provider}")
    if not body.api_key.strip():
        raise HTTPException(status_code=422, detail="API key must not be empty")

    key_name = "gemini_api_key" if body.provider == "gemini" else "xai_api_key"
    settings_store.set(key_name, body.api_key.strip())


@router.delete("/api-key/{provider}", status_code=204)
async def delete_api_key(provider: str) -> None:
    if provider not in PROVIDERS:
        raise HTTPException(status_code=422, detail=f"Unknown provider: {provider}")
    key_name = "gemini_api_key" if provider == "gemini" else "xai_api_key"
    settings_store.delete(key_name)


@router.put("/provider", status_code=204)
async def set_provider(body: ProviderUpdate) -> None:
    if body.provider not in PROVIDERS:
        raise HTTPException(status_code=422, detail=f"Unknown provider: {body.provider}")
    settings_store.set("ai_provider", body.provider)


@router.put("/model", status_code=204)
async def set_model(body: ModelUpdate) -> None:
    if body.provider == "gemini":
        if body.model not in gemini_service.AVAILABLE_MODELS:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown model. Available: {gemini_service.AVAILABLE_MODELS}",
            )
        settings_store.set("gemini_model", body.model)
    elif body.provider == "xai":
        if body.model not in xai_service.AVAILABLE_MODELS:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown model. Available: {xai_service.AVAILABLE_MODELS}",
            )
        settings_store.set("xai_model", body.model)
    else:
        raise HTTPException(status_code=422, detail=f"Unknown provider: {body.provider}")


@router.put("/style", status_code=204)
async def set_style(body: StyleUpdate) -> None:
    settings_store.set("generation_style", body.style.strip())


@router.get("/check")
async def check_connection() -> dict:
    """Test that the stored API key can reach the configured image provider API."""
    provider = settings_store.get("ai_provider", "gemini") or "gemini"
    if provider == "xai":
        return xai_service.check_connection()
