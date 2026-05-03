"""
Event slug generation + lookup utilities.
Generates SEO-friendly slugs like 'inter-vs-parma' for match events.
Handles duplicates (home/away matches) via numeric suffix: -2, -3, etc.
"""
import re
import unicodedata
from database import db


def _normalize(text: str) -> str:
    """Lowercase, remove accents, replace non-alphanumeric with dashes."""
    if not text:
        return ""
    # Lowercase + remove accents
    text = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    # Replace non-alphanumeric with dashes
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Strip leading/trailing dashes
    return text.strip("-")


def compute_base_slug(event: dict) -> str:
    """Compute base slug 'home-vs-away' from event doc."""
    home = _normalize(event.get("home_team") or "")
    away = _normalize(event.get("away_team") or "")
    if home and away:
        return f"{home}-vs-{away}"
    # Fallback to title if teams missing
    title = event.get("title")
    if isinstance(title, dict):
        title = title.get("it") or title.get("en") or ""
    return _normalize(title or "")


async def backfill_all_slugs() -> dict:
    """
    Generate and save slug for every event in DB.
    Order: events without slug first (preserve existing), then by sort_date to keep earliest match with clean slug.
    Returns stats.
    """
    # Sort by sort_date ASC so earliest match gets the clean slug
    cursor = db.events.find({}, {"_id": 1, "home_team": 1, "away_team": 1, "title": 1, "sort_date": 1, "slug": 1}).sort("sort_date", 1)

    updated = 0
    skipped = 0
    slugs_used = set()

    async for ev in cursor:
        base = compute_base_slug(ev)
        if not base:
            skipped += 1
            continue

        # Pick unique slug: if base already taken in THIS pass, append counter
        candidate = base
        counter = 1
        while candidate in slugs_used:
            counter += 1
            candidate = f"{base}-{counter}"
        slugs_used.add(candidate)

        # Save only if changed
        if ev.get("slug") != candidate:
            await db.events.update_one({"_id": ev["_id"]}, {"$set": {"slug": candidate}})
            updated += 1

    return {"updated": updated, "skipped": skipped, "total_slugs": len(slugs_used)}


async def find_event_by_slug(slug: str) -> dict | None:
    """Find event by slug. Returns event dict or None."""
    return await db.events.find_one({"slug": slug})
