"""
Google Gemini 3 Pro — JSON-LD Schema (Event/SportsEvent + AggregateOffer + BreadcrumbList + FAQPage).
"""
import json
import logging
from typing import Dict, Any, List
import httpx
from services.seo_keys import get_api_key

logger = logging.getLogger(__name__)
MODEL = "gemini-2.5-pro"  # Gemini 3 Pro alias (genai API: gemini-2.5-pro is the latest stable, gemini-3 in trial)


async def build_jsonld(target_type: str, ctx: Dict[str, Any], faq_items: List[Dict[str, str]] | None = None) -> Dict[str, Any]:
    """
    Restituisce uno schema JSON-LD compatibile Schema.org per il target.
    Tenta via Gemini con prompt strutturato; fallback procedurale se Gemini indisponibile.
    """
    api_key = await get_api_key("gemini")
    base_schema = _build_base_schema(target_type, ctx)
    # FAQ schema separato (sempre aggiunto se faq_items presenti)
    if faq_items:
        base_schema["mainEntity"] = _faq_main_entity(faq_items) if target_type != "event" else None
    if not api_key:
        return base_schema

    prompt = (
        f"Sei un esperto SEO Schema.org. Hai questo schema base JSON-LD:\n"
        f"{json.dumps(base_schema, ensure_ascii=False, indent=2)}\n\n"
        "Arricchiscilo aggiungendo i campi mancanti più rilevanti per Google Rich Snippets "
        "(es. AggregateOffer con priceCurrency 'EUR', lowPrice, availability, validFrom; "
        "sameAs Wikipedia se applicabile; description). "
        "NON inventare URL inesistenti, lascia 'sameAs' vuoto se non sei sicuro.\n\n"
        "Restituisci SOLO un JSON valido senza markdown, niente altro."
    )

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1500, "responseMimeType": "application/json"},
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key}"
    try:
        async with httpx.AsyncClient(timeout=60) as cx:
            r = await cx.post(url, json=body)
        if r.status_code == 200:
            data = r.json()
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            try:
                enriched = json.loads(text)
                # Re-attach FAQ entity if applicable
                if faq_items and target_type != "event":
                    enriched["mainEntity"] = _faq_main_entity(faq_items)
                return enriched
            except Exception as e:
                logger.error(f"Gemini JSON parse: {e}; text={text[:200]}")
        else:
            logger.warning(f"Gemini HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        logger.error(f"Gemini error: {e}")
    return base_schema


def _build_base_schema(target_type: str, ctx: Dict[str, Any]) -> Dict[str, Any]:
    title = ctx.get("title") or "?"
    if target_type == "event":
        h = ctx.get("home_team", "")
        a = ctx.get("away_team", "")
        return {
            "@context": "https://schema.org",
            "@type": "SportsEvent",
            "name": f"{h} vs {a}",
            "startDate": ctx.get("sort_date") or ctx.get("date"),
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "homeTeam": {"@type": "SportsTeam", "name": h},
            "awayTeam": {"@type": "SportsTeam", "name": a},
            "location": {
                "@type": "Place",
                "name": ctx.get("stadium", ""),
                "address": ctx.get("location", ""),
            },
            "offers": {
                "@type": "AggregateOffer",
                "priceCurrency": "EUR",
                "lowPrice": ctx.get("minimum_price") or "30",
                "availability": "https://schema.org/InStock",
                "url": ctx.get("canonical_url", ""),
            },
        }
    if target_type == "league":
        return {
            "@context": "https://schema.org",
            "@type": "SportsOrganization",
            "name": title,
            "sport": "Football",
            "areaServed": ctx.get("country", ""),
        }
    return {
        "@context": "https://schema.org",
        "@type": "SportsTeam",
        "name": title,
        "sport": "Football",
    }


def _faq_main_entity(faqs: List[Dict[str, str]]) -> Dict[str, Any]:
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f.get("q", ""),
                "acceptedAnswer": {"@type": "Answer", "text": f.get("a", "")},
            }
            for f in faqs if f.get("q")
        ],
    }
