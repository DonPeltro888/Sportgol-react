"""
DataForSEO — keyword volumes e SERP analysis (P0 essential).
"""
import logging
import httpx
from typing import Dict, List
from services.seo_keys import get_login_and_key

logger = logging.getLogger(__name__)


async def get_keyword_volumes(keywords: List[str], lang: str = "it", country: str = "IT") -> List[Dict]:
    """Volumi mensili per keyword. Lingua/paese ISO."""
    if not keywords:
        return []
    login, password = await get_login_and_key("dataforseo")
    if not login or not password:
        return []

    location_code = {"it": 2380, "en": 2826, "es": 2724}.get(lang.lower(), 2380)
    language_code = {"it": "it", "en": "en", "es": "es"}.get(lang.lower(), "it")

    body = [{
        "keywords": keywords[:50],
        "location_code": location_code,
        "language_code": language_code,
    }]
    auth = httpx.BasicAuth(login, password)
    try:
        async with httpx.AsyncClient(timeout=30, auth=auth) as cx:
            r = await cx.post(
                "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live",
                json=body,
            )
        if r.status_code == 200:
            data = r.json()
            tasks = data.get("tasks", [])
            if tasks and tasks[0].get("result"):
                return [
                    {
                        "keyword": item.get("keyword"),
                        "volume": item.get("search_volume", 0) or 0,
                        "cpc": item.get("cpc"),
                        "competition": item.get("competition"),
                    }
                    for item in tasks[0]["result"]
                ]
        logger.warning(f"DataForSEO HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        logger.error(f"DataForSEO error: {e}")
    return []


async def suggest_keywords(seed: str, lang: str = "it") -> Dict:
    """Genera keyword principali e correlate. P0: combina seed + suggerimenti DataForSEO Live SERP."""
    base = seed.strip()
    if not base:
        return {"primary": "", "related": []}

    primary_candidates = [
        f"biglietti {base}",
        f"biglietti {base} 2026",
        f"biglietti {base} prezzo",
        f"biglietti {base} stadio",
        f"{base} ticket",
    ]
    volumes = await get_keyword_volumes(primary_candidates, lang=lang)
    # Sort by volume desc
    volumes_sorted = sorted(volumes, key=lambda x: x.get("volume") or 0, reverse=True)
    primary = volumes_sorted[0]["keyword"] if volumes_sorted else f"biglietti {base}"
    related = [v["keyword"] for v in volumes_sorted[1:5] if v.get("keyword") and v["keyword"] != primary]
    return {
        "primary": primary,
        "related": related,
        "raw_volumes": volumes_sorted,
    }
