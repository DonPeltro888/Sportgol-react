"""
Gemini Nano Banana 2 (gemini-3.1-flash-image-preview) — generazione hero banner
1200x630 per pagine SEO ticketing calcio (squadre, leghe, eventi).

Output: salva PNG in /app/backend/uploads/seo/ e ritorna URL pubblico /uploads/seo/<filename>.
Uso EMERGENT_LLM_KEY (Universal Key) via emergentintegrations.
"""
import os
import base64
import logging
import re
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)
MODEL_ID = "gemini-3.1-flash-image-preview"
UPLOADS_DIR = Path("/app/backend/uploads/seo")
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:50]


def _build_prompt(target_type: str, ctx: Dict[str, Any]) -> str:
    """Prompt cinematico SEO-oriented per banner pulito 1200x630."""
    title = ctx.get("title") or ctx.get("name") or "?"
    home = ctx.get("home_team") or ""
    away = ctx.get("away_team") or ""
    stadium = ctx.get("stadium") or ""
    league = ctx.get("league") or ""

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
    # team
    return (
        f"Football team hero banner for '{title}'. "
        f"{'Home stadium ' + stadium + ', ' if stadium else ''}"
        f"shot at sunset with warm light, packed stands, abstract crowd silhouettes, "
        f"green football pitch in foreground. NO text, NO logos, NO jerseys, NO faces. "
        f"Atmosphere: passionate fanbase, premium ticketing. {base_style}"
    )


async def generate_hero(
    target_type: str,
    ctx: Dict[str, Any],
    slug: str,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Genera hero banner. Ritorna {url, filename, prompt, status}.
    Salva il file in /app/backend/uploads/seo/<slug>-<uuid8>.png.
    """
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        return {"status": "error", "error": "EMERGENT_LLM_KEY missing"}

    prompt = _build_prompt(target_type, ctx)
    session_id = f"seo-image-{uuid.uuid4().hex[:8]}"

    try:
        chat = LlmChat(api_key=api_key, session_id=session_id, system_message="You are a professional sports photography AI.")
        chat.with_model("gemini", MODEL_ID).with_params(modalities=["image", "text"])
        msg = UserMessage(text=prompt)
        text, images = await chat.send_message_multimodal_response(msg)
    except Exception as e:
        logger.error(f"Nano Banana generate error: {e}")
        return {"status": "error", "error": str(e)}

    if not images:
        return {"status": "error", "error": "No image returned by model"}

    # Salva la prima immagine
    img = images[0]
    try:
        image_bytes = base64.b64decode(img["data"])
    except Exception as e:
        return {"status": "error", "error": f"Base64 decode error: {e}"}

    filename = f"{_slugify(slug or target_type)}-{uuid.uuid4().hex[:8]}.png"
    file_path = UPLOADS_DIR / filename
    file_path.write_bytes(image_bytes)

    public_url = f"/api/seo/uploads/{filename}"
    if base_url:
        public_url = f"{base_url.rstrip('/')}{public_url}"

    logger.info(f"Hero image saved: {filename} ({len(image_bytes)} bytes)")
    return {
        "status": "success",
        "filename": filename,
        "url": public_url,
        "prompt": prompt[:200],
        "size_bytes": len(image_bytes),
    }
