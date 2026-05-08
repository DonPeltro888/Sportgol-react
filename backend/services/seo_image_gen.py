"""
Hero image generation via Google AI Studio direct API (Nano Banana / Gemini 2.5 Flash Image).

Endpoint diretto: https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent
Key: GEMINI_API_KEY (from .env) OR encrypted key 'gemini' in seo_api_keys collection.

Output: salva PNG in /app/backend/uploads/seo/ e ritorna URL pubblico /api/seo/uploads/<filename>.

NESSUNA DIPENDENZA da emergentintegrations / EMERGENT_LLM_KEY: il modulo è 100% portabile
e funziona con la stessa API key Google usata da seo_gemini.py.
"""
import base64
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

from services.seo_keys import get_api_key

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)
# Modello Nano Banana (Google AI Studio): https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash-image
MODEL_ID = os.getenv("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image-preview")
UPLOADS_DIR = Path("/app/backend/uploads/seo")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:50]


def _build_prompt(target_type: str, ctx: Dict[str, Any]) -> str:
    """Prompt cinematico SEO-oriented per banner pulito 1200x630."""
    title = ctx.get("title") or ctx.get("name") or "?"
    home = ctx.get("home_team") or ""
    away = ctx.get("away_team") or ""
    stadium = ctx.get("stadium") or ""

    base_style = (
        "Cinematic wide-format hero banner, 1200x630 aspect ratio, photorealistic, "
        "dramatic stadium lighting, vibrant colors, depth of field, motion blur, "
        "professional sports photography style. NO TEXT, NO LOGOS, NO LETTERS in image. "
        "Clean composition with negative space on the right side for SEO overlay text. "
        "Mood: epic, premium ticketing brand."
    )

    if target_type == "event":
        return (
            f"Football match hero banner: {home} vs {away} at {stadium}. "
            f"Show a packed stadium atmosphere with crowd silhouettes, stadium lights, "
            f"green football pitch in foreground, no players visible, no jerseys, "
            f"no text or logos. Atmosphere: night match, electric crowd energy. {base_style}"
        )
    if target_type == "league":
        country = ctx.get("country") or ""
        return (
            f"Football league hero banner for '{title}'{' (' + country + ')' if country else ''}. "
            f"Iconic top-tier football stadium aerial view at golden hour, vibrant green pitch, "
            f"packed stands with abstract crowd colors, dramatic sky. NO logos, NO text, NO jerseys. "
            f"{base_style}"
        )
    return (
        f"Football team hero banner for '{title}'. "
        f"{'Home stadium ' + stadium + ', ' if stadium else ''}"
        f"shot at sunset with warm light, packed stands, abstract crowd silhouettes, "
        f"green football pitch in foreground. NO text, NO logos, NO jerseys, NO faces. "
        f"Atmosphere: passionate fanbase, premium ticketing. {base_style}"
    )


async def _resolve_api_key() -> Optional[str]:
    """Cerca la key Gemini in ordine: env GEMINI_API_KEY → seo_api_keys('gemini')."""
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        return await get_api_key("gemini")
    except Exception:
        return None


async def generate_hero(
    target_type: str,
    ctx: Dict[str, Any],
    slug: str,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Genera hero banner via Google AI Studio direct API.
    Ritorna {url, filename, prompt, status, size_bytes}.
    Salva file in /app/backend/uploads/seo/<slug>-<uuid8>.png.
    """
    api_key = await _resolve_api_key()
    if not api_key:
        return {"status": "error", "error": "GEMINI_API_KEY missing (set in .env or in /admin/seo/api-tools)"}

    prompt = _build_prompt(target_type, ctx)
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        # Per Nano Banana: chiediamo image+text response. Il modello ritorna image bytes inline.
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
        },
    }
    url = ENDPOINT.format(model=MODEL_ID) + f"?key={api_key}"

    try:
        async with httpx.AsyncClient(timeout=120) as cx:
            r = await cx.post(url, json=body)
        if r.status_code != 200:
            logger.error(f"Nano Banana HTTP {r.status_code}: {r.text[:300]}")
            return {"status": "error", "error": f"HTTP {r.status_code}: {r.text[:200]}"}
        data = r.json()
    except Exception as e:
        logger.error(f"Nano Banana request error: {e}")
        return {"status": "error", "error": str(e)}

    # Parse response: cerca nel candidates[0].content.parts l'inlineData con mimeType image/*
    image_b64: Optional[str] = None
    try:
        candidates = data.get("candidates") or []
        if not candidates:
            return {"status": "error", "error": "no candidates in response"}
        parts = candidates[0].get("content", {}).get("parts", []) or []
        for p in parts:
            inline = p.get("inlineData") or p.get("inline_data") or {}
            mime = inline.get("mimeType") or inline.get("mime_type") or ""
            if "image" in mime and inline.get("data"):
                image_b64 = inline["data"]
                break
    except Exception as e:
        logger.error(f"Nano Banana parse error: {e}")
        return {"status": "error", "error": f"parse error: {e}"}

    if not image_b64:
        return {"status": "error", "error": "no image returned by model"}

    try:
        image_bytes = base64.b64decode(image_b64)
    except Exception as e:
        return {"status": "error", "error": f"base64 decode error: {e}"}

    filename = f"{_slugify(slug or target_type)}-{uuid.uuid4().hex[:8]}.png"
    file_path = UPLOADS_DIR / filename
    file_path.write_bytes(image_bytes)

    public_url = f"/api/seo/uploads/{filename}"
    if base_url:
        public_url = f"{base_url.rstrip('/')}{public_url}"

    logger.info(f"Hero image saved: {filename} ({len(image_bytes)} bytes) via direct Google AI Studio")
    return {
        "status": "success",
        "filename": filename,
        "url": public_url,
        "prompt": prompt[:200],
        "size_bytes": len(image_bytes),
        "model": MODEL_ID,
    }
