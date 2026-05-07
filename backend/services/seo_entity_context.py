"""
Helper per costruire il contesto SEO completo dato un entity (event/league/team):
- related_entities (per internal links Claude)
- breadcrumbs (per BreadcrumbList schema)
- canonical URL multi-lang
- geo (lat/lon stadio) — cache in db.seo_geo_cache
- same_as (Wikipedia URL) — cache in db.seo_entity_links
"""
import logging
from typing import Dict, Any, List, Optional
from database import db

logger = logging.getLogger(__name__)

BASE_URL = "https://golevents.com"


def canonical_url(target_type: str, doc: Dict[str, Any], lang: str = "it") -> str:
    slug = doc.get("slug") or ""
    if target_type == "event":
        if lang == "it":
            return f"{BASE_URL}/biglietti-{slug}"
        if lang == "en":
            return f"{BASE_URL}/{slug}-tickets"
        return f"{BASE_URL}/entradas-{slug}"
    if target_type == "league":
        return f"{BASE_URL}/{lang}/{slug}" if lang != "it" else f"{BASE_URL}/{slug}"
    # team
    if lang == "it":
        return f"{BASE_URL}/biglietti-{slug}"
    if lang == "en":
        return f"{BASE_URL}/{slug}-tickets"
    return f"{BASE_URL}/entradas-{slug}"


async def build_breadcrumbs(target_type: str, doc: Dict[str, Any], lang: str = "it") -> List[Dict[str, str]]:
    """Breadcrumbs per Schema.org."""
    items: List[Dict[str, str]] = [
        {"name": "Home", "url": BASE_URL + ("/" if lang == "it" else f"/{lang}")},
    ]
    if target_type == "event":
        league_name = doc.get("league") or ""
        league_slug = doc.get("league_slug") or _slugify(league_name)
        if league_name:
            items.append({"name": league_name, "url": f"{BASE_URL}/{league_slug}"})
        h, a = doc.get("home_team") or "", doc.get("away_team") or ""
        title = f"{h} vs {a}" if h and a else (doc.get("title") or "")
        items.append({"name": title, "url": canonical_url("event", doc, lang)})
    elif target_type == "league":
        items.append({"name": doc.get("name") or doc.get("title") or "", "url": canonical_url("league", doc, lang)})
    else:  # team
        league_name = doc.get("league") or ""
        league_slug = doc.get("league_slug") or _slugify(league_name)
        if league_name:
            items.append({"name": league_name, "url": f"{BASE_URL}/{league_slug}"})
        items.append({"name": doc.get("name") or doc.get("title") or "", "url": canonical_url("team", doc, lang)})
    return items


def _slugify(text: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")


async def fetch_related_entities(target_type: str, doc: Dict[str, Any], lang: str = "it") -> List[Dict[str, str]]:
    """
    Restituisce 5-8 entità correlate per costruire internal links REALI da DB:
    - event → home team, away team, league, prossimi 2 match della home, prossimi 2 della away
    - league → 5 squadre top + 2 prossimi match top
    - team → la lega + 3 prossimi match
    """
    out: List[Dict[str, str]] = []
    if target_type == "event":
        league_name = doc.get("league") or ""
        league_slug = doc.get("league_slug") or _slugify(league_name)
        h, a = doc.get("home_team") or "", doc.get("away_team") or ""
        for team_name in [h, a]:
            if not team_name:
                continue
            t_doc = await db.teams.find_one({"name": team_name}, {"_id": 0, "slug": 1, "name": 1})
            if t_doc and t_doc.get("slug"):
                out.append({
                    "kind": "team",
                    "label": t_doc["name"],
                    "url": canonical_url("team", t_doc, lang),
                })
        if league_slug:
            out.append({
                "kind": "league",
                "label": league_name,
                "url": f"{BASE_URL}/{league_slug}",
            })
        # prossimi match degli stessi team
        async for ev in db.events.find(
            {"$or": [{"home_team": h}, {"away_team": h}, {"home_team": a}, {"away_team": a}],
             "_id": {"$ne": doc.get("_id")}},
            {"_id": 0, "slug": 1, "home_team": 1, "away_team": 1}
        ).limit(4):
            if ev.get("slug"):
                out.append({
                    "kind": "match",
                    "label": f"{ev.get('home_team','')} vs {ev.get('away_team','')}",
                    "url": canonical_url("event", ev, lang),
                })
    elif target_type == "league":
        slug = doc.get("slug") or ""
        # top teams
        async for t in db.teams.find({"league_slug": slug}, {"_id": 0, "name": 1, "slug": 1}).limit(6):
            if t.get("slug"):
                out.append({
                    "kind": "team",
                    "label": t["name"],
                    "url": canonical_url("team", t, lang),
                })
        # next 2 events
        async for ev in db.events.find(
            {"league_slug": slug}, {"_id": 0, "slug": 1, "home_team": 1, "away_team": 1, "sort_date": 1}
        ).sort("sort_date", 1).limit(2):
            if ev.get("slug"):
                out.append({
                    "kind": "match",
                    "label": f"{ev.get('home_team','')} vs {ev.get('away_team','')}",
                    "url": canonical_url("event", ev, lang),
                })
    else:  # team
        league_name = doc.get("league") or ""
        league_slug = doc.get("league_slug") or _slugify(league_name)
        if league_slug:
            out.append({
                "kind": "league",
                "label": league_name or league_slug,
                "url": f"{BASE_URL}/{league_slug}",
            })
        team_name = doc.get("name") or doc.get("title") or ""
        async for ev in db.events.find(
            {"$or": [{"home_team": team_name}, {"away_team": team_name}]},
            {"_id": 0, "slug": 1, "home_team": 1, "away_team": 1, "sort_date": 1}
        ).sort("sort_date", 1).limit(4):
            if ev.get("slug"):
                out.append({
                    "kind": "match",
                    "label": f"{ev.get('home_team','')} vs {ev.get('away_team','')}",
                    "url": canonical_url("event", ev, lang),
                })

    # dedupe by URL
    seen = set()
    unique: List[Dict[str, str]] = []
    for it in out:
        u = it.get("url")
        if u and u not in seen:
            seen.add(u)
            unique.append(it)
    return unique[:8]


async def get_geo_for_stadium(stadium: str) -> Optional[Dict[str, Any]]:
    """Cache lookup geo (lat/lon) per stadio. Prima DB cache, poi Perplexity fallback."""
    if not stadium:
        return None
    key = stadium.strip().lower()
    cached = await db.seo_geo_cache.find_one({"_id": key}, {"_id": 0})
    if cached and cached.get("latitude") and cached.get("longitude"):
        return {
            "latitude": cached["latitude"],
            "longitude": cached["longitude"],
            "city": cached.get("city"),
            "country": cached.get("country"),
            "postal_code": cached.get("postal_code"),
        }
    # fallback Perplexity (lazy import to avoid cycles)
    try:
        from services.seo_perplexity import lookup_geo
        result = await lookup_geo(stadium)
        if result and result.get("latitude"):
            await db.seo_geo_cache.update_one(
                {"_id": key},
                {"$set": {**result, "stadium": stadium}},
                upsert=True,
            )
            return result
    except Exception as e:
        logger.warning(f"Perplexity geo lookup failed for {stadium}: {e}")
    return None


async def get_same_as(entity_name: str, kind: str = "team") -> List[str]:
    """Recupera Wikipedia/Wikidata/site URL per entity (cache 30gg)."""
    if not entity_name:
        return []
    key = f"{kind}:{entity_name.strip().lower()}"
    cached = await db.seo_entity_links.find_one({"_id": key}, {"_id": 0})
    if cached and cached.get("urls"):
        return cached["urls"]
    try:
        from services.seo_perplexity import lookup_same_as
        urls = await lookup_same_as(entity_name, kind)
        if urls:
            await db.seo_entity_links.update_one(
                {"_id": key},
                {"$set": {"urls": urls, "kind": kind, "name": entity_name}},
                upsert=True,
            )
            return urls
    except Exception as e:
        logger.warning(f"Perplexity sameAs lookup failed for {entity_name}: {e}")
    return []
