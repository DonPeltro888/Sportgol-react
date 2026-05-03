"""
Sync via OpenFootball (https://github.com/openfootball/football.json).
JSON pubblici su GitHub, gratis, illimitati, no key.
Copertura: top leghe nazionali (EN/IT/ES/DE/FR) - intera stagione 380 match/lega.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import httpx
from database import db
from services.matchesio_sync import (
    STANDARD_SECTORS, STADIUM_IMAGES, BIG_CLUBS,
    normalize_team, ensure_league_in_db,
)

logger = logging.getLogger(__name__)

OPENFOOTBALL_BASE = "https://raw.githubusercontent.com/openfootball/football.json/master"

ITA_DAYS = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
ITA_MONTHS = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
              "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

# (file_slug, season, db_slug, league_name, country, type, order)
COMPETITIONS_OF: List[Tuple[str, str, str, str, str, str, int]] = [
    ("en.1",  "2025-26", "premier-league",  "PREMIER LEAGUE", "England",   "league", 2),
    ("it.1",  "2025-26", "serie-a",         "SERIE A",        "Italy",     "league", 1),
    ("es.1",  "2025-26", "la-liga",         "LA LIGA",        "Spain",     "league", 3),
    ("de.1",  "2025-26", "bundesliga",      "BUNDESLIGA",     "Germany",   "league", 4),
    ("fr.1",  "2025-26", "ligue-1",         "LIGUE 1",        "France",    "league", 5),
    ("nl.1",  "2025-26", "eredivisie",      "EREDIVISIE",     "Netherlands", "league", 8),
    ("pt.1",  "2025-26", "liga-portugal",   "LIGA PORTUGAL",  "Portugal",  "league", 6),
]


def _fmt_ita_date(date_str: str, time_str: str = "") -> str:
    """'2026-05-20' → 'Mercoledì, 20 Maggio 2026'."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{ITA_DAYS[dt.weekday()]}, {dt.day} {ITA_MONTHS[dt.month]} {dt.year}"
    except Exception:
        return date_str


def _build_event(match: Dict, league_name: str) -> Optional[Dict]:
    home = (match.get("team1") or "").strip()
    away = (match.get("team2") or "").strip()
    if not home or not away:
        return None
    date_str = match.get("date", "")
    time_str = match.get("time", "")
    
    # OpenFootball ID stabile: combinazione date+teams
    of_id = f"of-{date_str}-{normalize_team(home).lower().replace(' ', '_')}-vs-{normalize_team(away).lower().replace(' ', '_')}"
    
    home_n = normalize_team(home)
    away_n = normalize_team(away)
    title = f"{home_n} vs {away_n}"
    big = (home_n in BIG_CLUBS or away_n in BIG_CLUBS)
    img_idx = (hash(of_id) % len(STADIUM_IMAGES))
    
    iso_date = f"{date_str}T{time_str or '20:00'}:00" if date_str else ""
    
    return {
        "matchesio_id": of_id,
        "source": "openfootball",
        "title": title,
        "league": league_name,
        "home_team": home_n,
        "away_team": away_n,
        "stadium": "TBA",
        "location": "TBA",
        "date": _fmt_ita_date(date_str, time_str),
        "time": time_str,
        "sort_date": iso_date,
        "categories": [c for c in [home_n, away_n, league_name] if c],
        "ticket_categories": [{**s} for s in STANDARD_SECTORS],
        "image": STADIUM_IMAGES[img_idx],
        "is_big_match": big,
        "tags": [],
    }


async def sync_via_openfootball() -> Dict:
    """Sync top leghe nazionali da OpenFootball GitHub JSON."""
    started_at = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stats = {
        "started_at": started_at,
        "source": "openfootball",
        "total_inserted": 0,
        "total_updated": 0,
        "leagues_synced": 0,
        "leagues_failed": [],
        "leagues_empty": [],
        "per_league": {},
        "logos_added": 0,
        "sample_inserted": [],
    }
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        for (file_slug, season, db_slug, league_name, country, league_type, order) in COMPETITIONS_OF:
            try:
                await ensure_league_in_db(db_slug, league_name, country, league_type, order)
                url = f"{OPENFOOTBALL_BASE}/{season}/{file_slug}.json"
                resp = await client.get(url)
                if resp.status_code != 200:
                    stats["leagues_empty"].append({"league": league_name, "reason": f"HTTP {resp.status_code} on {url}"})
                    continue
                
                data = resp.json()
                matches = data.get("matches", [])
                
                # Filtra solo eventi futuri
                future_matches = [m for m in matches if m.get("date", "") >= today]
                stats["per_league"][league_name] = len(future_matches)
                
                if not future_matches:
                    stats["leagues_empty"].append({"league": league_name, "reason": "Nessun match futuro nella stagione"})
                    continue
                
                inserted = 0
                updated = 0
                for m in future_matches:
                    ev = _build_event(m, league_name)
                    if not ev:
                        continue
                    existing = await db.events.find_one({"matchesio_id": ev["matchesio_id"]}, {"_id": 1})
                    if existing:
                        await db.events.update_one(
                            {"_id": existing["_id"]},
                            {"$set": {**{k: v for k, v in ev.items() if k != "matchesio_id"},
                                      "updated_at": datetime.now(timezone.utc).isoformat()}}
                        )
                        updated += 1
                    else:
                        ev["created_at"] = datetime.now(timezone.utc).isoformat()
                        await db.events.insert_one(ev)
                        inserted += 1
                        if len(stats["sample_inserted"]) < 10:
                            stats["sample_inserted"].append({
                                "title": ev["title"], "league": league_name,
                                "date": ev["date"], "stadium": ev["stadium"],
                            })
                
                stats["total_inserted"] += inserted
                stats["total_updated"] += updated
                stats["leagues_synced"] += 1
            except Exception as e:
                logger.exception(f"OpenFootball errore {league_name}: {e}")
                stats["leagues_failed"].append({"league": league_name, "error": str(e)[:200]})
    
    # Backfill slug
    try:
        from services.event_slug import backfill_all_slugs
        slug_stats = await backfill_all_slugs()
        stats["slugs_updated"] = slug_stats.get("updated", 0)
    except Exception as e:
        stats["slug_error"] = str(e)
    
    stats["finished_at"] = datetime.now(timezone.utc).isoformat()
    stats["total_in_db"] = await db.events.count_documents({})
    stats["success"] = True
    
    await db.sync_logs.insert_one({**stats, "log_at": datetime.now(timezone.utc), "source": "openfootball"})
    return stats
