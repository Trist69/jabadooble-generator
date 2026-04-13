"""
xAI image generation service.

Model: grok-imagine-image
SDK: REST API via httpx

Flow
────
1. generate_image() — image call: generate a cartoon illustration for a single subject
2. check_connection() — verify the stored xAI API key can reach the inference API
"""

from __future__ import annotations

import base64

import httpx

from app.core.settings_store import get as get_setting

_XAI_API_BASE = "https://api.x.ai/v1"
_STYLE = (
    "cute colourful cartoon illustration, children's sticker style, "
    "simple clean design, white background, no text, centred subject"
)

AVAILABLE_MODELS = [
    "grok-imagine-image",
]


def _headers() -> dict[str, str]:
    key = get_setting("xai_api_key")
    if not key:
        raise ValueError(
            "xAI API key is not configured. Go to Settings and enter your xAI API key."
        )
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _model() -> str:
    return get_setting("xai_model", AVAILABLE_MODELS[0]) or AVAILABLE_MODELS[0]


def generate_image(subject: str, style: str | None = None) -> bytes:
    effective_style = style or get_setting("generation_style", _STYLE)
    prompt = f"{subject}. Style: {effective_style}."
    payload = {
        "model": _model(),
        "prompt": prompt,
    }

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(
            f"{_XAI_API_BASE}/images/generations",
            headers=_headers(),
            json=payload,
        )

        if resp.status_code != 200:
            raise ValueError(
                f"xAI image generation failed ({resp.status_code}): {resp.text}"
            )

        body = resp.json()
        data = body.get("data")
        if not data or not isinstance(data, list):
            raise ValueError("xAI returned no image data")

        image_obj = data[0]
        if image_obj is None:
            raise ValueError("xAI returned an empty image object")

        image_url = image_obj.get("url")
        if image_url:
            download = client.get(image_url)
            if download.status_code != 200:
                raise ValueError(
                    f"Failed to download generated xAI image: {download.status_code}"
                )
            return download.content

        b64_data = image_obj.get("image") or image_obj.get("b64_json")
        if isinstance(b64_data, str):
            return base64.b64decode(b64_data)

        raise ValueError("xAI returned no image URL or base64 payload")


def check_connection() -> dict:
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(f"{_XAI_API_BASE}/models", headers=_headers())
            if resp.status_code != 200:
                return {"ok": False, "error": resp.text}

        return {"ok": True, "model": _model(), "response": "xAI API reachable"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
