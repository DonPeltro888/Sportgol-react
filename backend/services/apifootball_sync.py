"""
Sync via APIfootball.com (https://apifootball.com).
Trial 15 giorni gratis con accesso UEL/UECL/Coppa Italia/FA Cup/Copa del Rey.
Dopo trial: $21/mese (European plan).
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

import httpx
from database import db
from services.matchesio_sync import (
    STANDARD_SECTORS, STADIUM_IMAGES, BIG_CLUBS,
    normalize_team, ensure_league_in_db,
)

logger = logging.getLogger(__name__)

APIFOOTBALL_BASE = "https://apiv3.apifootball.com"

ITA_DAYS = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
ITA_MONTHS = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
              "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

# (league_id, db_slug, league_name, country, type, order)
COMPETITIONS_AF: List[Tuple[int, str, str, str, str, int]] = [
    # COPPE EUROPEE
    (3,   "champions-league",   "CHAMPIONS LEAGUE",   "Europe",        "cup",    70),
    (4,   "europa-league",      "EUROPA LEAGUE",      "Europe",        "cup",    71),
    # COPPE NAZIONALI
    (205, "coppa-italia",       "COPPA ITALIA",       "Italy",         "cup",    50),
    (300, "copa-del-rey",       "COPA DEL REY",       "Spain",         "cup",    51),
    (146, "fa-cup",             "FA CUP",             "England",       "cup",    52),
    # MONDIALI
    (28,  "fifa-world-cup-2026", "FIFA WORLD CUP 2026", "USA / Canada / Mexico", "cup", 90),
    # AFC / CAF
    (727, "afc-champions-league", "AFC CHAMPIONS LEAGUE", "Asia",         "cup", 97),
    (10,  "afc-champions-league-elite", "AFC CHAMPIONS LEAGUE ELITE", "Asia", "cup", 98),
    (346, "caf-champions-league", "CAF CHAMPIONS LEAGUE", "Africa",       "cup", 95),
    # ALTRE LEGHE
    (152, "premier-league",     "PREMIER LEAGUE",     "England",       "league",  2),
    (207, "serie-a",            "SERIE A",            "Italy",         "league",  1),
    (302, "la-liga",            "LA LIGA",            "Spain",         "league",  3),
    (175, "bundesliga",         "BUNDESLIGA",         "Germany",       "league",  4),
    (153, "championship",       "CHAMPIONSHIP",       "England",       "league", 20),
]


async def _get_apifootball_key() -> Optional[str]:
    """Ritorna la API key apifootball.com dal DB."""
    doc = await db.settings.find_one({"_id": "integrations"}, {"_id": 0})
    if not doc:
        return None
    af = doc.get("apifootball", {})
    if not af.get("enabled") or not af.get("api_key"):
        return None
    return af["api_key"]


def _fmt_ita_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{ITA_DAYS[dt.weekday()]}, {dt.day} {ITA_MONTHS[dt.month]} {dt.year}"
    except Exception:
        return date_str


def _build_event(m: Dict, league_name: str) -> Optional[Dict]:
    home = (m.get("match_hometeam_name") or "").strip()
    away = (m.get("match_awayteam_name") or "").strip()
    if not home or not away:
        return None
    
    match_id = str(m.get("match_id") or "")
    date_str = m.get("match_date", "")
    time_str = m.get("match_time", "")
    home_logo = m.get("team_home_badge")
    away_logo = m.get("team_away_badge")
    stadium = m.get("match_stadium") or "TBA"
    
    home_n = normalize_team(home)
    away_n = normalize_team(away)
    title = f"{home_n} vs {away_n}"
    big = (home_n in BIG_CLUBS or away_n in BIG_CLUBS)
    img_idx = (hash(match_id) % len(STADIUM_IMAGES))
    
    iso_date = f"{date_str}T{time_str or '20:00'}:00" if date_str else ""
    
    return {
        "matchesio_id": f"af-{match_id}",
        "source": "apifootball",
        "title": title,
        "league": league_name,
        "home_team": home_n,
        "away_team": away_n,
        "home_team_logo_src": home_logo,
        "away_team_logo_src": away_logo,
        "stadium": stadium,
        "location": "TBA",
        "date": _fmt_ita_date(date_str),
        "time": time_str,
        "sort_date": iso_date,
        "categories": [c for c in [home_n, away_n, league_name] if c],
        "ticket_categories": [{**s} for s in STANDARD_SECTORS],
        "image": STADIUM_IMAGES[img_idx],
        "is_big_match": big,
        "tags": [],
    }


async def sync_via_apifootball(only_empty_leagues: Optional[List[str]] = None) -> Dict:
    """Sync via APIfootball.com per coppe/leghe configurate."""
    api_key = await _get_apifootball_key()
    if not api_key:
        return {"success": False, "error": "API key APIfootball.com non configurata. Vai in Admin → Integrazioni API."}
    
    started_at = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    end_date = (datetime.now(timezone.utc) + timedelta(days=180)).strftime("%Y-%m-%d")
    
    stats = {
        "started_at": started_at,
        "source": "apifootball",
        "total_inserted": 0,
        "total_updated": 0,
        "leagues_synced": 0,
        "leagues_failed": [],
        "leagues_empty": [],
        "per_league": {},
        "logos_added": 0,
        "sample_inserted": [],
    }
    
    target = COMPETITIONS_AF
    if only_empty_leagues:
        target_set = {n.upper().strip() for n in only_empty_leagues}
        target = [c for c in COMPETITIONS_AF if c[2].upper().strip() in target_set]
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        for (league_id, db_slug, league_name, country, league_type, order) in target:
            try:
                await ensure_league_in_db(db_slug, league_name, country, league_type, order)
                resp = await client.get(
                    APIFOOTBALL_BASE,
                    params={
                        "action": "get_events",
                        "from": today,
                        "to": end_date,
                        "league_id": league_id,
                        "APIkey": api_key,
                    },
                )
                if resp.status_code != 200:
                    stats["leagues_failed"].append({"league": league_name, "error": f"HTTP {resp.status_code}"})
                    continue
                
                data = resp.json()
                # APIfootball restituisce array oppure dict con error
                if isinstance(data, dict):
                    if "error" in data or "message" in data:
                        # Error response - skip but log
                        stats["leagues_empty"].append({"league": league_name, "reason": data.get("message") or str(data)[:100]})
                        continue
                    matches = []
                else:
                    matches = data
                
                stats["per_league"][league_name] = len(matches)
                if not matches:
                    stats["leagues_empty"].append({"league": league_name, "reason": "0 eventi nei prossimi 180 giorni"})
                    continue
                
                inserted = 0
                updated = 0
                for m in matches:
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
                    
                    # Loghi
                    for team_name, logo_url in [
                        (ev["home_team"], ev.get("home_team_logo_src")),
                        (ev["away_team"], ev.get("away_team_logo_src")),
                    ]:
                        if team_name and logo_url:
                            res = await db.teams.update_one(
                                {"name": team_name, "$or": [{"logo_url": ""}, {"logo_url": None}, {"logo_url": {"$exists": False}}]},
                                {"$set": {"logo_url": logo_url, "logo_source": "apifootball"}},
                            )
                            if res.modified_count:
                                stats["logos_added"] += 1
                
                stats["total_inserted"] += inserted
                stats["total_updated"] += updated
                stats["leagues_synced"] += 1
            except Exception as e:
                logger.exception(f"APIfootball errore {league_name}: {e}")
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
    
    await db.sync_logs.insert_one({**stats, "log_at": datetime.now(timezone.utc), "source": "apifootball"})
    return stats


async def test_apifootball_connection() -> Dict:
    """Test la key APIfootball.com."""
    api_key = await _get_apifootball_key()
    if not api_key:
        return {"ok": False, "error": "Nessuna key configurata"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(APIFOOTBALL_BASE, params={"action": "get_leagues", "APIkey": api_key})
            if resp.status_code != 200:
                return {"ok": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
            data = resp.json()
            if isinstance(data, list):
                return {
                    "ok": True,
                    "provider": "APIfootball.com",
                    "leagues_available": len(data),
                    "note": f"{len(data)} leghe accessibili. Trial scade dopo 15gg dalla registrazione, poi $21/mese.",
                }
            return {"ok": False, "error": data.get("message", str(data)[:200])}
    except Exception as e:
        return {"ok": False, "error": str(e)}
