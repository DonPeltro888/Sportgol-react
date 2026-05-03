"""
Sync via TheSportsDB (https://www.thesportsdb.com).
Free tier: key pubblica "3", 15 eventi/lega per stagione.
Premium: $3/mese su Patreon (key personale, eventi illimitati).
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

ITA_DAYS = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
ITA_MONTHS = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
              "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

# (sportsdb_id, db_slug, league_name, country, type, order)
COMPETITIONS_SDB: List[Tuple[int, str, str, str, str, int]] = [
    (4481, "europa-league",      "EUROPA LEAGUE",      "Europe",        "cup", 71),
    (5071, "conference-league",  "CONFERENCE LEAGUE",  "Europe",        "cup", 72),
    (4480, "champions-league",   "CHAMPIONS LEAGUE",   "Europe",        "cup", 70),
    (4506, "coppa-italia",       "COPPA ITALIA",       "Italy",         "cup", 50),
    (4525, "fa-cup",             "FA CUP",             "England",       "cup", 52),
]


async def _get_sportsdb_key() -> str:
    """Ritorna la API key TheSportsDB. Default '3' (free pubblica)."""
    doc = await db.settings.find_one({"_id": "integrations"}, {"_id": 0})
    if not doc:
        return "3"
    sdb = doc.get("sportsdb", {})
    if sdb.get("api_key") and sdb.get("enabled", True):
        return sdb["api_key"]
    return "3"


def _fmt_ita_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{ITA_DAYS[dt.weekday()]}, {dt.day} {ITA_MONTHS[dt.month]} {dt.year}"
    except Exception:
        return date_str


def _build_event(m: Dict, league_name: str) -> Optional[Dict]:
    home = (m.get("strHomeTeam") or "").strip()
    away = (m.get("strAwayTeam") or "").strip()
    if not home or not away:
        return None
    
    sdb_id = str(m.get("idEvent") or "")
    date_str = m.get("dateEvent", "")
    time_str = (m.get("strTime") or "").split(":")
    time_hm = f"{time_str[0]}:{time_str[1]}" if len(time_str) >= 2 else "20:00"
    home_logo = m.get("strHomeTeamBadge")
    away_logo = m.get("strAwayTeamBadge")
    stadium = m.get("strVenue") or "TBA"
    
    home_n = normalize_team(home)
    away_n = normalize_team(away)
    title = f"{home_n} vs {away_n}"
    big = (home_n in BIG_CLUBS or away_n in BIG_CLUBS)
    img_idx = (hash(sdb_id) % len(STADIUM_IMAGES))
    
    iso_date = f"{date_str}T{time_hm}:00" if date_str else ""
    
    return {
        "matchesio_id": f"sdb-{sdb_id}",
        "source": "thesportsdb",
        "title": title,
        "league": league_name,
        "home_team": home_n,
        "away_team": away_n,
        "home_team_logo_src": home_logo,
        "away_team_logo_src": away_logo,
        "stadium": stadium,
        "location": "TBA",
        "date": _fmt_ita_date(date_str),
        "time": time_hm,
        "sort_date": iso_date,
        "categories": [c for c in [home_n, away_n, league_name] if c],
        "ticket_categories": [{**s} for s in STANDARD_SECTORS],
        "image": STADIUM_IMAGES[img_idx],
        "is_big_match": big,
        "tags": [],
    }


async def sync_via_thesportsdb(only_empty_leagues: Optional[List[str]] = None) -> Dict:
    """Sync coppe da TheSportsDB."""
    api_key = await _get_sportsdb_key()
    started_at = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    stats = {
        "started_at": started_at,
        "source": "thesportsdb",
        "api_key_used": "free (pubblica)" if api_key == "3" else "premium personale",
        "total_inserted": 0,
        "total_updated": 0,
        "leagues_synced": 0,
        "leagues_failed": [],
        "leagues_empty": [],
        "per_league": {},
        "logos_added": 0,
        "sample_inserted": [],
    }
    
    target = COMPETITIONS_SDB
    if only_empty_leagues:
        target_set = {n.upper().strip() for n in only_empty_leagues}
        target = [c for c in COMPETITIONS_SDB if c[2].upper().strip() in target_set]
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for (sdb_id, db_slug, league_name, country, league_type, order) in target:
            try:
                await ensure_league_in_db(db_slug, league_name, country, league_type, order)
                url = f"https://www.thesportsdb.com/api/v1/json/{api_key}/eventsseason.php"
                resp = await client.get(url, params={"id": sdb_id, "s": "2025-2026"})
                if resp.status_code != 200:
                    stats["leagues_failed"].append({"league": league_name, "error": f"HTTP {resp.status_code}"})
                    continue
                
                data = resp.json()
                events = data.get("events") or []
                # Solo futuri
                future = [e for e in events if (e.get("dateEvent") or "") >= today]
                stats["per_league"][league_name] = len(future)
                
                if not future:
                    stats["leagues_empty"].append({"league": league_name, "reason": f"0 eventi futuri (totali stagione: {len(events)})"})
                    continue
                
                inserted = 0
                updated = 0
                for m in future:
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
                    
                    for team_name, logo_url in [
                        (ev["home_team"], ev.get("home_team_logo_src")),
                        (ev["away_team"], ev.get("away_team_logo_src")),
                    ]:
                        if team_name and logo_url:
                            res = await db.teams.update_one(
                                {"name": team_name, "$or": [{"logo_url": ""}, {"logo_url": None}, {"logo_url": {"$exists": False}}]},
                                {"$set": {"logo_url": logo_url, "logo_source": "thesportsdb"}},
                            )
                            if res.modified_count:
                                stats["logos_added"] += 1
                
                stats["total_inserted"] += inserted
                stats["total_updated"] += updated
                stats["leagues_synced"] += 1
            except Exception as e:
                logger.exception(f"TheSportsDB errore {league_name}: {e}")
                stats["leagues_failed"].append({"league": league_name, "error": str(e)[:200]})
    
    try:
        from services.event_slug import backfill_all_slugs
        slug_stats = await backfill_all_slugs()
        stats["slugs_updated"] = slug_stats.get("updated", 0)
    except Exception as e:
        stats["slug_error"] = str(e)
    
    stats["finished_at"] = datetime.now(timezone.utc).isoformat()
    stats["total_in_db"] = await db.events.count_documents({})
    stats["success"] = True
    
    await db.sync_logs.insert_one({**stats, "log_at": datetime.now(timezone.utc), "source": "thesportsdb"})
    return stats
