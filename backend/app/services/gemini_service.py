"""
Gemini AI image generation service.

Model: gemini-2.5-flash-image  (a.k.a. "Nano Banana 🍌")
Free tier: 500 images / day, 10 RPM
SDK: google-genai  (pip install google-genai)

Flow
────
1. generate_subjects()  — text call: given a theme, produce N distinct
                          child-friendly subject labels (one per Dobble symbol)
2. generate_image()     — image call: generate a cartoon illustration
                          for a single subject label

Both calls use the same API key from the settings store.
"""

from __future__ import annotations

import io
import json
import re
import time
import random

from google import genai
from google.genai import types

from app.core.settings_store import get as get_setting

# ── Default generation style ──────────────────────────────────────────────
_STYLE = (
    "cute colourful cartoon illustration, children's sticker style, "
    "simple clean design, white background, no text, centred subject"
)

# Supported Nano Banana models (newest first)
AVAILABLE_MODELS = [
    "gemini-2.5-flash-image",           # GA — production, free tier
    "gemini-2.0-flash-preview-image-generation",  # older preview (fallback)
]


def _retry_on_failure(func, max_retries=3, base_delay=1.0):
    """Retry a function call on failure with exponential backoff."""
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as exc:
            if attempt == max_retries:
                raise
            # Check if it's a retryable server error (503, high demand) but NOT quota exceeded
            error_str = str(exc).lower()
            if ('resource_exhausted' in error_str or 'quota exceeded' in error_str or 
                'quota_exceeded' in error_str):
                # Don't retry quota/rate limit errors - they need user action
                raise
            elif ('503' in error_str or 'unavailable' in error_str or 
                  'high demand' in error_str or 'temporary' in error_str):
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
            else:
                # Don't retry for other errors (like auth, invalid input, etc.)
                raise


def _client() -> genai.Client:
    key = get_setting("gemini_api_key")
    if not key:
        raise ValueError(
            "Gemini API key is not configured. "
            "Go to Settings and enter your Google AI Studio key."
        )
    return genai.Client(api_key=key)


def _model() -> str:
    return get_setting("gemini_model", AVAILABLE_MODELS[0]) or AVAILABLE_MODELS[0]


# ── Subject generation ────────────────────────────────────────────────────


def generate_subjects(theme: str, count: int) -> list[str]:
    """
    Use Gemini text output to produce `count` distinct, child-friendly
    subject names for a Dobble symbol theme.

    Returns a list of short labels, e.g. ["Lion", "Elephant", "Giraffe", …]
    Falls back to numbered placeholders if the model response can't be parsed.
    """
    def _call():
        client = _client()
        prompt = (
            f"List exactly {count} distinct, child-friendly subjects for the theme: '{theme}'.\n"
            "Rules:\n"
            "- Each subject should work as a standalone cute cartoon illustration.\n"
            "- Short names only (1-3 words), no descriptions.\n"
            "- Return ONLY a JSON array of strings, nothing else.\n"
            f'Example for theme "animals": ["Lion", "Elephant", "Parrot", ...]\n'
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",       # text-only call — cheapest model
            contents=prompt,
        )
        text = (response.text or "").strip()

        # Extract JSON array from response (may be wrapped in markdown code block)
        match = re.search(r"\[.*?\]", text, re.DOTALL)
        if match:
            try:
                subjects = json.loads(match.group())
                if isinstance(subjects, list) and subjects:
                    return [str(s).strip() for s in subjects[:count]]
            except json.JSONDecodeError:
                pass

        # Fallback: numbered subjects
        return [f"{theme} {i + 1}" for i in range(count)]

    return _retry_on_failure(_call, max_retries=5)


def generate_image(subject: str, style: str | None = None) -> bytes:
    """
    Generate a single PNG image for `subject` using Nano Banana 🍌.

    Returns raw PNG bytes.
    Raises ValueError if the model returns no image part.
    """
    def _call():
        client = _client()
        effective_style = style or get_setting("generation_style", _STYLE)
        prompt = f"{subject}. Style: {effective_style}."

        response = client.models.generate_content(
            model=_model(),
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                data = part.inline_data.data
                # SDK may return bytes or base64 str
                if isinstance(data, bytes):
                    return data
                import base64
                return base64.b64decode(data)

        raise ValueError(f"Gemini returned no image for subject: {subject!r}")

    return _retry_on_failure(_call, max_retries=5)


# ── Health check ──────────────────────────────────────────────────────────


def check_connection() -> dict:
    """Verify the API key works with a minimal text call."""
    def _call():
        client = _client()
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'ok' in one word.",
        )
        return {"ok": True, "model": _model(), "response": (resp.text or "").strip()}

    try:
        return _retry_on_failure(_call, max_retries=5)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
