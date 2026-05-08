"""
AI Validator — Perplexity per metadati team + Gemini Vision per logo verification.
"""
import os
import json
import re
import base64
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

from database import db
from services.seo_keys import get_api_key

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
logger = logging.getLogger(__name__)

LOGO_CACHE_DIR = Path("/app/backend/uploads/team_logos")
LOGO_CACHE_DIR.mkdir(parents=True, exist_ok=True)


async def validate_team_via_perplexity(team_name: str, league_hint: str = "") -> Dict[str, Any]:
    """
    Chiede a Perplexity i metadati ufficiali del team.
    Cache 30gg in db.team_validation_cache.
    """
    if not team_name:
        return {}
    cache_key = f"{team_name.lower()}|{league_hint.lower()}"
    cached = await db.team_validation_cache.find_one({"_id": cache_key}, {"_id": 0})
    if cached and (datetime.now(timezone.utc).timestamp() - cached.get("ts", 0)) < 30 * 86400:
        return cached.get("data", {})

    api_key = await get_api_key("perplexity")
    if not api_key:
        return {}

    prompt = (
        f"Fornisci i metadati UFFICIALI della squadra di calcio '{team_name}'"
        f"{' (lega: ' + league_hint + ')' if league_hint else ''}. "
        "Restituisci SOLO un JSON valido senza markdown nel formato esatto:\n"
        '{"official_name": "Inter Milan", "stadium": "Giuseppe Meazza", '
        '"city": "Milano", "country": "IT", "league": "Serie A", '
        '"wikipedia_url": "https://it.wikipedia.org/wiki/...", '
        '"official_website": "https://www.inter.it", '
        '"logo_url": "https://.../inter-logo.png"}\n'
        "Per logo_url usa preferibilmente Wikipedia/Wikidata Commons. "
        "Se non sei sicuro al 100% di un campo, omettilo."
    )
    body = {
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500,
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=45) as cx:
            r = await cx.post("https://api.perplexity.ai/chat/completions", headers=headers, json=body)
        if r.status_code in (200, 201):
            text = r.json()["choices"][0]["message"]["content"]
            text = text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```\w*\n?", "", text)
                text = re.sub(r"\n?```$", "", text).strip()
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if m:
                data = json.loads(m.group(0))
                if isinstance(data, dict):
                    await db.team_validation_cache.update_one(
                        {"_id": cache_key},
                        {"$set": {"data": data, "ts": datetime.now(timezone.utc).timestamp()}},
                        upsert=True,
                    )
                    return data
        else:
            logger.warning(f"Perplexity validate HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        logger.error(f"validate_team_via_perplexity error: {e}")
    return {}


async def verify_logo_with_gemini(team_name: str, logo_url: str) -> Dict[str, Any]:
    """
    Usa Gemini 2.5 Pro Vision via direct Google AI Studio API per verificare se logo_url
    è davvero il logo di team_name. Ritorna {match: 'yes'|'no'|'uncertain', confidence: 0-1, reason}.

    Key precedence: env GEMINI_API_KEY → seo_api_keys('gemini').
    """
    if not team_name or not logo_url:
        return {"match": "uncertain", "confidence": 0, "reason": "missing inputs"}

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or await get_api_key("gemini")
    )
    if not api_key:
        return {"match": "uncertain", "confidence": 0,
                "reason": "GEMINI_API_KEY missing (set in .env or in /admin/seo/api-tools)"}

    # Download logo as bytes
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as cx:
            r = await cx.get(logo_url, headers={"User-Agent": WIKI_USER_AGENT})
        if r.status_code != 200 or not r.content:
            return {"match": "uncertain", "confidence": 0,
                    "reason": f"logo fetch HTTP {r.status_code}"}
        ct = (r.headers.get("content-type") or "image/png").split(";")[0].strip().lower()
        if "image" not in ct and "octet-stream" not in ct:
            return {"match": "uncertain", "confidence": 0,
                    "reason": f"unexpected content-type: {ct}"}
        if ct == "application/octet-stream":
            ct = "image/png"
        img_b64 = base64.b64encode(r.content).decode("utf-8")
    except Exception as e:
        return {"match": "uncertain", "confidence": 0, "reason": f"logo download fail: {e}"}

    # Build Gemini Vision request (direct Google AI Studio API)
    prompt = (
        f"Analyze this image and tell me: is this the OFFICIAL logo/badge of the football team '{team_name}'? "
        "Look at colors, shape, letters, animals, symbols. "
        "Respond ONLY with a valid JSON object: "
        '{"match": "yes" | "no" | "uncertain", "confidence": 0.0 to 1.0, '
        '"reason": "short explanation", "detected_team": "name of team you see in logo (if recognizable)"}. '
        "No markdown, no code fences."
    )
    body = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inlineData": {"mimeType": ct, "data": img_b64}},
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": 400,
            "responseMimeType": "application/json",
        },
    }
    model = os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-pro")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    try:
        async with httpx.AsyncClient(timeout=60) as cx:
            resp = await cx.post(url, json=body)
        if resp.status_code != 200:
            return {"match": "uncertain", "confidence": 0,
                    "reason": f"Gemini Vision HTTP {resp.status_code}: {resp.text[:200]}"}
        data = resp.json()
        text = (data.get("candidates", [{}])[0]
                    .get("content", {}).get("parts", [{}])[0]
                    .get("text", "")).strip()
        if text.startswith("```"):
            text = re.sub(r"^```\w*\n?", "", text)
            text = re.sub(r"\n?```$", "", text).strip()
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            parsed = json.loads(m.group(0))
            if isinstance(parsed, dict):
                return {
                    "match": parsed.get("match", "uncertain"),
                    "confidence": float(parsed.get("confidence") or 0),
                    "reason": parsed.get("reason", "")[:200],
                    "detected_team": parsed.get("detected_team", "")[:100],
                }
    except Exception as e:
        logger.error(f"verify_logo_with_gemini error: {e}")
        return {"match": "uncertain", "confidence": 0, "reason": str(e)[:200]}

    return {"match": "uncertain", "confidence": 0, "reason": "no parseable response"}


def _normalize_wikimedia_url(url: str) -> str:
    """
    Forza tutti gli URL Wikimedia ad usare Special:FilePath (PNG renderizzato),
    che ha un'image policy meno restrittiva degli upload.wikimedia.org diretti.
    """
    if not url:
        return url
    # wiki/File:NAME → Special:FilePath/NAME
    m = re.match(r"https?://(?:[a-z]+\.)?(?:wikipedia|commons)\.(?:wikimedia\.)?org/wiki/File:(.+?)(?:\?.*)?$", url)
    if m:
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{m.group(1)}?width=400"
    # upload.wikimedia.org/wikipedia/commons/X/YY/NAME.svg → Special:FilePath/NAME.svg?width=400
    m = re.match(r"https?://upload\.wikimedia\.org/wikipedia/(?:commons|en|it|es)/(?:thumb/)?[a-f0-9]/[a-f0-9]{2}/([^/?]+?)(?:/\d+px-[^/?]+)?(?:\?.*)?$", url)
    if m:
        return f"https://commons.wikimedia.org/wiki/Special:FilePath/{m.group(1)}?width=400"
    return url


WIKI_USER_AGENT = "GoLeventsBot/1.0 (https://golevents.com; admin@golevents.com)"


async def _is_valid_image_url(url: str) -> bool:
    """Verifica che l'URL ritorni un'immagine valida."""
    if not url or not url.startswith("http"):
        return False
    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True) as cx:
            r = await cx.get(url, headers={"User-Agent": WIKI_USER_AGENT})
        if r.status_code == 200 and len(r.content) > 1000:
            ct = (r.headers.get("content-type") or "").lower()
            if "image" in ct or "octet-stream" in ct:
                return True
    except Exception:
        pass
    return False


async def find_alternative_logo(team_name: str) -> Optional[str]:
    """
    Cerca un logo URL alternativo VALIDATO via Perplexity multi-candidate.
    NB: TheSportsDB free API è bugged (ritorna sempre Arsenal), quindi NON viene usato.
    Ritorna l'URL ORIGINALE validato (es. Wikimedia Special:FilePath).
    Per servirlo nel browser, il chiamante deve fare proxy via /api/seo/logo-proxy.
    """
    api_key = await get_api_key("perplexity")
    if not api_key:
        return None
    prompt = (
        f"Trova il logo ufficiale (badge/stemma) della squadra di calcio '{team_name}'. "
        "Restituisci SOLO un JSON array di 4-6 URL CANDIDATI (preferibilmente Wikimedia Commons, "
        "siti ufficiali del club, Wikipedia infobox image). I file devono essere PNG/SVG/JPG "
        "diretti (non pagine HTML). Esempio formato: "
        '["https://upload.wikimedia.org/wikipedia/commons/thumb/.../logo.svg/200px-logo.svg.png", '
        '"https://www.acmilan.com/.../logo.png"]. '
        "Se non sei sicuro al 100% di un URL, OMETTILO. Nessun markdown."
    )
    body = {
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    candidates: list[str] = []
    try:
        async with httpx.AsyncClient(timeout=45) as cx:
            r = await cx.post("https://api.perplexity.ai/chat/completions", headers=headers, json=body)
        if r.status_code in (200, 201):
            text = r.json()["choices"][0]["message"]["content"].strip()
            if text.startswith("```"):
                text = re.sub(r"^```\w*\n?", "", text)
                text = re.sub(r"\n?```$", "", text).strip()
            m = re.search(r"\[.*\]", text, re.DOTALL)
            if m:
                arr = json.loads(m.group(0))
                if isinstance(arr, list):
                    candidates = [u for u in arr if isinstance(u, str) and u.startswith("http")][:8]
                    # Normalize Wikimedia URLs (wiki/File:X → Special:FilePath/X)
                    candidates = [_normalize_wikimedia_url(u) for u in candidates]
    except Exception as e:
        logger.warning(f"perplexity candidates err: {e}")

    # Valida candidati uno per uno fino a trovare il primo che funziona
    for url in candidates:
        if await _is_valid_image_url(url):
            logger.info(f"find_alternative_logo: {team_name} → {url}")
            return url

    # Fallback: chiedi a validate_team_via_perplexity (ha cache)
    val = await validate_team_via_perplexity(team_name)
    candidate = val.get("logo_url")
    if candidate and await _is_valid_image_url(candidate):
        return candidate

    logger.warning(f"find_alternative_logo: NO valid logo for '{team_name}'")
    return None


async def download_and_cache_logo(remote_url: str, slug: str) -> Optional[str]:
    """
    Scarica il logo da remote_url (con UA Wikimedia-compliant) e lo salva
    in /app/backend/uploads/team_logos/{slug}.png. Ritorna URL pubblico
    /api/seo/team-logo/{slug}.png da servire nel browser.
    """
    if not remote_url or not slug:
        return None
    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as cx:
            r = await cx.get(remote_url, headers={"User-Agent": WIKI_USER_AGENT})
        if r.status_code != 200 or len(r.content) < 1000:
            return None
        ct = (r.headers.get("content-type") or "").lower()
        if "image" not in ct and "octet-stream" not in ct:
            return None
        # Determina extension dal content-type
        ext = "png"
        if "svg" in ct:
            ext = "svg"
        elif "jpeg" in ct or "jpg" in ct:
            ext = "jpg"
        elif "webp" in ct:
            ext = "webp"
        filename = f"{slug}.{ext}"
        out_path = LOGO_CACHE_DIR / filename
        out_path.write_bytes(r.content)
        logger.info(f"Logo cached: {filename} ({len(r.content)} bytes)")
        return f"/api/seo/team-logo/{filename}"
    except Exception as e:
        logger.warning(f"download_and_cache_logo error for {slug}: {e}")
        return None
