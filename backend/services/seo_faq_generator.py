"""
AI FAQ Generator + FAQPage JSON-LD Schema (BIG SEO WIN — rich snippets).

Per ogni entità (event/team/league) genera 5-8 FAQ contestualmente rilevanti
usando Claude Sonnet 4.5. Salva in `seo_meta.{lang}.faq` come array di {q, a}.
Frontend SeoSchemaInjector aggiunge automaticamente FAQPage schema.org → Google rich snippet boost.

Esempi FAQ generati:
- Event "Inter vs Milan": "When is Inter vs Milan played?", "How much do tickets cost?", "Where is the stadium?", etc.
- Team "Real Madrid": "When does Real Madrid play next?", "What is Real Madrid's stadium?", etc.
- League "Serie A": "When does Serie A 2025-26 start?", "Where to buy Serie A tickets?", etc.
"""
import json
import logging
import re
from typing import Dict, List, Any, Optional

import httpx
from services.seo_keys import get_api_key
from database import db

logger = logging.getLogger(__name__)
MODEL = "claude-sonnet-4-5"


def _build_prompt(entity_type: str, entity: Dict[str, Any], lang: str) -> str:
    lang_full = {"it": "Italian", "en": "English", "es": "Spanish"}.get(lang, "English")
    if entity_type == "event":
        ctx = (
            f"Football event: {entity.get('home_team','?')} vs {entity.get('away_team','?')} "
            f"on {entity.get('date','?')} at {entity.get('stadium','?')} ({entity.get('location','?')}). "
            f"League: {entity.get('league','?')}."
        )
    elif entity_type == "team":
        ctx = (
            f"Football club: {entity.get('name','?')} from {entity.get('city','?')}, "
            f"{entity.get('country','?')}. League: {entity.get('league_slug','?')}. "
            f"Stadium: {entity.get('stadium','?')}."
        )
    else:  # league
        ctx = (
            f"Football league: {entity.get('name','?')} ({entity.get('country','?')}). "
            f"Type: {entity.get('type','league')}."
        )

    return (
        f"You are a senior SEO copywriter for a football ticketing website. "
        f"Generate exactly 6 FAQ entries in {lang_full} optimized for Google's 'People Also Ask' "
        f"and FAQPage rich snippets. Context: {ctx}\n\n"
        f"Each FAQ must be:\n"
        f"- A natural search query a real fan would type (NOT marketing copy)\n"
        f"- Answer 50-90 words, factual, helpful\n"
        f"- Cover: timing, ticket info, stadium, transport, seating, official availability\n"
        f"- Include the entity name in at least 3 questions\n\n"
        f"Return ONLY valid JSON array, no markdown:\n"
        f'[{{"q":"...","a":"..."}}, ...]'
    )


async def generate_faq_for_entity(
    entity_type: str, entity: Dict[str, Any], langs: List[str] = None
) -> Dict[str, List[Dict[str, str]]]:
    """Genera FAQ in N lingue. Ritorna {lang: [{q,a}]}."""
    langs = langs or ["it", "en", "es"]
    api_key = await get_api_key("claude")
    if not api_key:
        return {}

    out: Dict[str, List[Dict[str, str]]] = {}
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    async with httpx.AsyncClient(timeout=90) as cx:
        for lang in langs:
            prompt = _build_prompt(entity_type, entity, lang)
            try:
                r = await cx.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json={"model": MODEL, "max_tokens": 2000, "messages": [{"role": "user", "content": prompt}]},
                )
                if r.status_code != 200:
                    logger.warning(f"FAQ Claude HTTP {r.status_code}: {r.text[:200]}")
                    continue
                text = r.json()["content"][0]["text"]
            except Exception as e:
                logger.warning(f"FAQ generation error {lang}: {e}")
                continue

            m = re.search(r"\[\s*\{.*?\}\s*\]", text, re.DOTALL)
            if not m:
                continue
            try:
                items = json.loads(m.group(0))
                out[lang] = [{"q": x["q"], "a": x["a"]} for x in items if isinstance(x, dict) and x.get("q") and x.get("a")][:6]
            except json.JSONDecodeError:
                continue
    return out


async def generate_and_save_faq(
    entity_type: str, slug: str, langs: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Genera FAQ e salva in db.{collection}.seo_meta.{lang}.faq"""
    coll_map = {"event": "events", "team": "teams", "league": "leagues"}
    coll_name = coll_map.get(entity_type)
    if not coll_name:
        return {"ok": False, "error": "invalid entity_type"}
    coll = db[coll_name]
    doc = await coll.find_one({"slug": slug}, {"_id": 0})
    if not doc:
        return {"ok": False, "error": f"{entity_type} '{slug}' not found"}

    faqs = await generate_faq_for_entity(entity_type, doc, langs)
    if not faqs:
        return {"ok": False, "error": "AI generation failed (no FAQ produced)"}

    set_ops: Dict[str, Any] = {}
    for lang, items in faqs.items():
        set_ops[f"seo_meta.{lang}.faq"] = items

    await coll.update_one({"slug": slug}, {"$set": set_ops})
    return {
        "ok": True,
        "entity_type": entity_type,
        "slug": slug,
        "langs_generated": list(faqs.keys()),
        "faq_counts": {k: len(v) for k, v in faqs.items()},
        "preview": faqs.get("it", faqs.get("en", []))[:2],
    }


async def get_faq(entity_type: str, slug: str, lang: str = "it") -> List[Dict[str, str]]:
    """Helper per il frontend / schema injector."""
    coll_map = {"event": "events", "team": "teams", "league": "leagues"}
    coll = db[coll_map.get(entity_type, "events")]
    doc = await coll.find_one({"slug": slug}, {"_id": 0, "seo_meta": 1})
    if not doc:
        return []
    return ((doc.get("seo_meta") or {}).get(lang) or {}).get("faq") or []
