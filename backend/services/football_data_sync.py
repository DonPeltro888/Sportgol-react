"""
Sync eventi tramite Football-Data.org (provider alternativo, gratis senza carta).
Free tier: 10 req/min, copre 14 competizioni top:
  WC, CL, EL, EC, BL1, DED, BSA, PD, FL1, ELC, PPL, SA, PL, CLI
"""
import asyncio
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

FD_BASE = "https://api.football-data.org/v4"

ITA_DAYS = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
ITA_MONTHS = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
              "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

# Mapping competizioni Football-Data.org → DB.
# (fd_code, db_slug, league_name, country, type, order)
COMPETITIONS_FD: List[Tuple[str, str, str, str, str, int]] = [
    # Coppe europee (priorità ALTA: matchesio le ha vuote)
    ("CL",  "champions-league",   "CHAMPIONS LEAGUE",   "Europe",        "cup",    70),
    ("EL",  "europa-league",      "EUROPA LEAGUE",      "Europe",        "cup",    71),
    ("EC",  "euro-championship",  "EURO CHAMPIONSHIP",  "Europe",        "cup",    92),
    # Top leghe nazionali (matchesio le ha già, qui aggiorniamo dati)
    ("SA",  "serie-a",            "SERIE A",            "Italy",         "league",  1),
    ("PL",  "premier-league",     "PREMIER LEAGUE",     "England",       "league",  2),
    ("PD",  "la-liga",            "LA LIGA",            "Spain",         "league",  3),
    ("BL1", "bundesliga",         "BUNDESLIGA",         "Germany",       "league",  4),
    ("FL1", "ligue-1",            "LIGUE 1",            "France",        "league",  5),
    ("DED", "eredivisie",         "EREDIVISIE",         "Netherlands",   "league",  8),
    ("PPL", "liga-portugal",      "LIGA PORTUGAL",      "Portugal",      "league",  6),
    ("ELC", "championship",       "CHAMPIONSHIP",       "England",       "league", 20),
    # Internazionali
    ("WC",  "fifa-world-cup-2026", "FIFA WORLD CUP 2026", "USA / Canada / Mexico", "cup", 90),
    ("BSA", "brasileirao",        "BRASILEIRÃO",        "Brazil",        "league", 33),
    ("CLI", "copa-libertadores",  "COPA LIBERTADORES",  "South America", "cup",    96),
]


async def _get_fd_api_key() -> Optional[str]:
    """Ritorna la API key football-data.org dal DB se configurata."""
    doc = await db.settings.find_one({"_id": "integrations"}, {"_id": 0})
    if not doc:
        return None
    fa = doc.get("football_api", {})
    if fa.get("provider") != "football_data" or not fa.get("enabled") or not fa.get("api_key"):
        return None
    return fa["api_key"]


def _fmt_ita_date_from_iso(iso_dt: str) -> str:
    """Converte ISO datetime → 'Mercoledì, 20 Maggio 2026'."""
    try:
        dt = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
        return f"{ITA_DAYS[dt.weekday()]}, {dt.day} {ITA_MONTHS[dt.month]} {dt.year}"
    except Exception:
        return iso_dt


async def _fetch_matches_fd(client: httpx.AsyncClient, code: str, api_key: str) -> List[Dict]:
    """Scarica fixtures SCHEDULED+TIMED (futuri) da Football-Data.org."""
    try:
        resp = await client.get(
            f"{FD_BASE}/competitions/{code}/matches",
            headers={"X-Auth-Token": api_key},
            params={"status": "SCHEDULED,TIMED"},
            timeout=20.0,
        )
        if resp.status_code == 429:
            logger.warning(f"FD: rate limit per {code}, sleep 70s e retry")
            await asyncio.sleep(70)
            resp = await client.get(
                f"{FD_BASE}/competitions/{code}/matches",
                headers={"X-Auth-Token": api_key},
                params={"status": "SCHEDULED,TIMED"},
                timeout=20.0,
            )
        if resp.status_code == 403:
            logger.warning(f"FD: competizione {code} non disponibile nel piano (403)")
            return []
        if resp.status_code != 200:
            logger.warning(f"FD: HTTP {resp.status_code} per {code}: {resp.text[:200]}")
            return []
        data = resp.json()
        return data.get("matches", []) or []
    except Exception as e:
        logger.error(f"FD fetch error {code}: {e}")
        return []


def _build_event_from_fd(match: Dict, league_name: str) -> Optional[Dict]:
    """Trasforma un match Football-Data.org nel formato evento del nostro DB."""
    home = match.get("homeTeam", {}).get("name") or ""
    away = match.get("awayTeam", {}).get("name") or ""
    home_logo = match.get("homeTeam", {}).get("crest")
    away_logo = match.get("awayTeam", {}).get("crest")
    if not home or not away:
        return None
    if "TBD" in home.upper() or "TBD" in away.upper():
        # Lasciamo TBD perché finali UEL/UCL hanno questo formato fino a semifinali
        pass

    iso_date = match.get("utcDate") or ""
    match_id = str(match.get("id"))
    venue = match.get("venue") or ""
    # Football-Data non sempre ha city, deduciamo
    city = ""

    home_n = normalize_team(home)
    away_n = normalize_team(away)
    title = f"{home_n} vs {away_n}"
    big = (home_n in BIG_CLUBS or away_n in BIG_CLUBS)
    img_idx = (hash(match_id) % len(STADIUM_IMAGES))

    return {
        "matchesio_id": f"fd-{match_id}",  # prefisso fd- (Football-Data)
        "source": "football_data",
        "title": title,
        "league": league_name,
        "home_team": home_n,
        "away_team": away_n,
        "home_team_logo_src": home_logo,
        "away_team_logo_src": away_logo,
        "stadium": venue or "TBA",
        "location": city or "TBA",
        "date": _fmt_ita_date_from_iso(iso_date),
        "time": iso_date[11:16] if len(iso_date) >= 16 else "",
        "sort_date": iso_date,
        "categories": [c for c in [home_n, away_n, league_name] if c],
        "ticket_categories": [{**s} for s in STANDARD_SECTORS],
        "image": STADIUM_IMAGES[img_idx],
        "is_big_match": big,
        "tags": [],
    }


async def sync_via_football_data(only_empty_leagues: Optional[List[str]] = None) -> Dict:
    """
    Sync eventi via Football-Data.org.
    Args:
        only_empty_leagues: se fornita, sincronizza SOLO le leghe nei nomi specificati.
                           Utile come "fill missing" dopo matchesio.
    """
    api_key = await _get_fd_api_key()
    if not api_key:
        return {"success": False, "error": "API key Football-Data.org non configurata o disabilitata."}

    started_at = datetime.now(timezone.utc).isoformat()
    stats = {
        "started_at": started_at,
        "source": "football_data",
        "total_inserted": 0,
        "total_updated": 0,
        "leagues_synced": 0,
        "leagues_failed": [],
        "leagues_empty": [],
        "leagues_skipped_not_in_filter": [],
        "per_league": {},
        "logos_added": 0,
        "sample_inserted": [],
    }

    # Filter target competitions (case-insensitive match su league_name)
    target = COMPETITIONS_FD
    if only_empty_leagues:
        target_set = {n.upper().strip() for n in only_empty_leagues}
        target = [c for c in COMPETITIONS_FD if c[2].upper().strip() in target_set]
        for c in COMPETITIONS_FD:
            if c[2].upper().strip() not in target_set:
                stats["leagues_skipped_not_in_filter"].append(c[2])

    async with httpx.AsyncClient(timeout=20.0) as client:
        # Sequential con sleep 7s per rispettare 10 req/min free tier
        for (code, db_slug, league_name, country, league_type, order) in target:
            try:
                await ensure_league_in_db(db_slug, league_name, country, league_type, order)
                matches = await _fetch_matches_fd(client, code, api_key)
                stats["per_league"][league_name] = len(matches)

                if not matches:
                    stats["leagues_empty"].append({"league": league_name, "reason": f"FD ha restituito 0 eventi (code={code})"})
                    await asyncio.sleep(7)
                    continue

                inserted = 0
                updated = 0
                for m in matches:
                    ev = _build_event_from_fd(m, league_name)
                    if not ev:
                        continue
                    existing = await db.events.find_one({"matchesio_id": ev["matchesio_id"]}, {"_id": 1})
                    if existing:
                        await db.events.update_one(
                            {"_id": existing["_id"]},
                            {"$set": {
                                **{k: v for k, v in ev.items() if k != "matchesio_id"},
                                "updated_at": datetime.now(timezone.utc).isoformat(),
                            }}
                        )
                        updated += 1
                    else:
                        ev["created_at"] = datetime.now(timezone.utc).isoformat()
                        from services.db_normalize import insert_event
                        await insert_event(ev)
                        inserted += 1
                        if len(stats["sample_inserted"]) < 10:
                            stats["sample_inserted"].append({
                                "title": ev["title"],
                                "league": league_name,
                                "date": ev["date"],
                                "stadium": ev["stadium"],
                            })

                    # Logo squadre
                    for team_name, logo_url in [
                        (ev["home_team"], ev.get("home_team_logo_src")),
                        (ev["away_team"], ev.get("away_team_logo_src")),
                    ]:
                        if team_name and logo_url:
                            res = await db.teams.update_one(
                                {"name": team_name, "$or": [{"logo_url": ""}, {"logo_url": None}, {"logo_url": {"$exists": False}}]},
                                {"$set": {"logo_url": logo_url, "logo_source": "football_data"}},
                            )
                            if res.modified_count:
                                stats["logos_added"] += 1

                stats["total_inserted"] += inserted
                stats["total_updated"] += updated
                stats["leagues_synced"] += 1
                # Rispetta rate limit free tier: 10 req/min → sleep 7s tra una e l'altra
                await asyncio.sleep(7)
            except Exception as e:
                logger.exception(f"Errore FD sync {league_name}: {e}")
                stats["leagues_failed"].append({"league": league_name, "error": str(e)[:200]})
                await asyncio.sleep(7)

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

    await db.sync_logs.insert_one({**stats, "log_at": datetime.now(timezone.utc), "source": "football_data"})
    return stats
