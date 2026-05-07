"""
Sync eventi/loghi tramite API-Football (RapidAPI) o Football-Data.org.
Primario rispetto a matchesio.com. Loghi inclusi nei dati API.

Mapping competizioni nostre → API-Football league IDs.
Riferimento: https://www.api-football.com/documentation-v3
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import httpx
from database import db
from services.matchesio_sync import (
    STANDARD_SECTORS, STADIUM_IMAGES, BIG_CLUBS,
    normalize_team, fmt_ita_date, ensure_league_in_db,
)

logger = logging.getLogger(__name__)

API_FOOTBALL_BASE = "https://api-football-v1.p.rapidapi.com/v3"
API_FOOTBALL_HOST = "api-football-v1.p.rapidapi.com"

# Mapping nostre competizioni → API-Football league IDs.
# (api_football_id, season, db_slug, league_name, country, type, order)
# Season default: corrente (es. 2025 = stagione 2025/26).
# Riferimento ID: https://api-football-v1.p.rapidapi.com/v3/leagues
COMPETITIONS_AF: List[Tuple[int, int, str, str, str, str, int]] = [
    # ===== TOP 7 LEAGUES =====
    (135,  2025, "serie-a",            "SERIE A",            "Italy",    "league",  1),
    (39,   2025, "premier-league",     "PREMIER LEAGUE",     "England",  "league",  2),
    (140,  2025, "la-liga",            "LA LIGA",            "Spain",    "league",  3),
    (78,   2025, "bundesliga",         "BUNDESLIGA",         "Germany",  "league",  4),
    (61,   2025, "ligue-1",            "LIGUE 1",            "France",   "league",  5),
    (94,   2025, "liga-portugal",      "LIGA PORTUGAL",      "Portugal", "league",  6),
    (203,  2025, "super-lig",          "SUPER LIG",          "Turkey",   "league",  7),
    # ===== ALTRE LEGHE EUROPEE =====
    (88,   2025, "eredivisie",         "EREDIVISIE",         "Netherlands", "league",  8),
    (144,  2025, "jupiler-pro-league", "JUPILER PRO LEAGUE", "Belgium",     "league",  9),
    (40,   2025, "championship",       "CHAMPIONSHIP",       "England",     "league", 20),
    (79,   2025, "2-bundesliga",       "2. BUNDESLIGA",      "Germany",     "league", 21),
    (62,   2025, "ligue-2",            "LIGUE 2",            "France",      "league", 22),
    # ===== LEGHE EXTRA-EUROPA =====
    (253,  2026, "mls",                "MLS",                "USA",         "league", 30),
    (262,  2025, "liga-mx",            "LIGA MX",            "Mexico",      "league", 31),
    (98,   2026, "j1-league",          "J1 LEAGUE",          "Japan",       "league", 32),
    # ===== COPPE NAZIONALI =====
    (137,  2025, "coppa-italia",       "COPPA ITALIA",       "Italy",      "cup",    50),
    (143,  2025, "copa-del-rey",       "COPA DEL REY",       "Spain",      "cup",    51),
    (45,   2025, "fa-cup",             "FA CUP",             "England",    "cup",    52),
    (81,   2025, "dfb-pokal",          "DFB POKAL",          "Germany",    "cup",    53),
    (66,   2025, "coupe-de-france",    "COUPE DE FRANCE",    "France",     "cup",    54),
    # ===== COPPE EUROPEE =====
    (2,    2025, "champions-league",   "CHAMPIONS LEAGUE",   "Europe",     "cup",    70),
    (3,    2025, "europa-league",      "EUROPA LEAGUE",      "Europe",     "cup",    71),
    (848,  2025, "conference-league",  "CONFERENCE LEAGUE",  "Europe",     "cup",    72),
    (5,    2024, "uefa-nations-league", "UEFA NATIONS LEAGUE", "Europe",   "cup",    73),
    # ===== INTERNAZIONALI =====
    (1,    2026, "fifa-world-cup-2026", "FIFA WORLD CUP 2026", "USA / Canada / Mexico", "cup", 90),
    (15,   2025, "fifa-club-world-cup", "FIFA CLUB WORLD CUP", "International", "cup", 91),
    (4,    2024, "euro-championship",   "EURO CHAMPIONSHIP",   "Europe",        "cup", 92),
    (9,    2024, "copa-america",        "COPA AMERICA",        "South America", "cup", 93),
    (6,    2025, "africa-cup-of-nations", "AFRICA CUP OF NATIONS", "Africa",    "cup", 94),
    (13,   2025, "copa-libertadores",   "COPA LIBERTADORES",   "South America", "cup", 96),
    (17,   2025, "afc-champions-league", "AFC CHAMPIONS LEAGUE", "Asia",        "cup", 97),
]

ITA_DAYS = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
ITA_MONTHS = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
              "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]


def _fmt_ita_date_from_iso(iso_dt: str) -> str:
    """Converte ISO datetime '2026-05-20T19:00:00+00:00' → 'Mercoledì, 20 Maggio 2026'."""
    try:
        dt = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
        return f"{ITA_DAYS[dt.weekday()]}, {dt.day} {ITA_MONTHS[dt.month]} {dt.year}"
    except Exception:
        return iso_dt


async def _get_api_key() -> Optional[Tuple[str, str]]:
    """Ritorna (api_key, provider) dal DB o None se non configurata/disabilitata."""
    doc = await db.settings.find_one({"_id": "integrations"}, {"_id": 0})
    if not doc:
        return None
    fa = doc.get("football_api", {})
    if not fa.get("enabled") or not fa.get("api_key"):
        return None
    return (fa["api_key"], fa.get("provider", "api_football"))


async def _fetch_fixtures_af(
    client: httpx.AsyncClient, league_id: int, season: int, api_key: str
) -> List[Dict]:
    """Scarica fixtures da API-Football per una lega+stagione."""
    try:
        resp = await client.get(
            f"{API_FOOTBALL_BASE}/fixtures",
            headers={
                "X-RapidAPI-Key": api_key,
                "X-RapidAPI-Host": API_FOOTBALL_HOST,
            },
            params={"league": league_id, "season": season},
            timeout=20.0,
        )
        if resp.status_code != 200:
            logger.warning(f"API-Football: HTTP {resp.status_code} for league={league_id}: {resp.text[:200]}")
            return []
        data = resp.json()
        return data.get("response", []) or []
    except Exception as e:
        logger.error(f"API-Football fetch error league={league_id}: {e}")
        return []


def _build_event_from_af(fixture: Dict, league_name: str) -> Optional[Dict]:
    """Trasforma una fixture API-Football nel formato evento del nostro DB."""
    fx = fixture.get("fixture", {})
    teams = fixture.get("teams", {})
    home = teams.get("home", {}).get("name") or ""
    away = teams.get("away", {}).get("name") or ""
    home_logo = teams.get("home", {}).get("logo")
    away_logo = teams.get("away", {}).get("logo")
    if not home or not away:
        return None

    iso_date = fx.get("date") or ""
    venue = fx.get("venue", {}) or {}
    stadium = venue.get("name") or ""
    city = venue.get("city") or ""
    fixture_id = str(fx.get("id"))

    # Skip past matches: API-Football ha status NS, FT, etc.
    status = (fx.get("status") or {}).get("short", "")
    if status in {"FT", "AET", "PEN", "ABD", "AWD", "WO", "CANC"}:
        return None

    title = f"{home} vs {away}"
    home_n = normalize_team(home)
    away_n = normalize_team(away)
    big = (home_n in BIG_CLUBS or away_n in BIG_CLUBS)

    img_idx = (hash(fixture_id) % len(STADIUM_IMAGES))
    return {
        "matchesio_id": f"af-{fixture_id}",  # prefisso af- per origine
        "source": "api_football",
        "title": title,
        "league": league_name,
        "home_team": home_n,
        "away_team": away_n,
        "home_team_logo_src": home_logo,
        "away_team_logo_src": away_logo,
        "stadium": stadium,
        "location": city,
        "date": _fmt_ita_date_from_iso(iso_date),
        "time": iso_date[11:16] if len(iso_date) >= 16 else "",
        "sort_date": iso_date,
        "categories": [c for c in [home_n, away_n, league_name] if c],
        "ticket_categories": [{**s} for s in STANDARD_SECTORS],
        "image": STADIUM_IMAGES[img_idx],
        "is_big_match": big,
        "tags": [],
        "status_source": status,
    }


async def sync_via_api_football() -> Dict:
    """
    Sync eventi via API-Football. Logica:
    - Recupera api_key dal DB (settings.integrations.football_api).
    - Fetch parallelo di tutte le COMPETITIONS_AF.
    - Upsert per matchesio_id="af-{fixture_id}" (così non collide con matchesio).
    - Aggiorna logo squadra in db.teams se assente.
    """
    cred = await _get_api_key()
    if not cred:
        return {"success": False, "error": "API key non configurata o disabilitata. Vai in Admin → Integrazioni API."}
    api_key, provider = cred
    if provider != "api_football":
        return {"success": False, "error": f"Provider '{provider}' non ancora supportato per sync. Usa api_football."}

    started_at = datetime.now(timezone.utc).isoformat()
    stats = {
        "started_at": started_at,
        "source": "api_football",
        "total_inserted": 0,
        "total_updated": 0,
        "leagues_synced": 0,
        "leagues_failed": [],
        "leagues_empty": [],
        "per_league": {},
        "logos_added": 0,
        "sample_inserted": [],  # primi 10 nuovi eventi inseriti
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        for (league_id, season, db_slug, league_name, country, league_type, order) in COMPETITIONS_AF:
            try:
                await ensure_league_in_db(db_slug, league_name, country, league_type, order)
                fixtures = await _fetch_fixtures_af(client, league_id, season, api_key)
                stats["per_league"][league_name] = len(fixtures)

                if not fixtures:
                    stats["leagues_empty"].append({"league": league_name, "reason": "API ha restituito 0 eventi"})
                    continue

                inserted = 0
                updated = 0
                for fx in fixtures:
                    ev = _build_event_from_af(fx, league_name)
                    if not ev:
                        continue

                    # Upsert per matchesio_id (af-{id})
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
                        # Salva esempio (max 10 totali)
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
                                {"$set": {"logo_url": logo_url, "logo_source": "api_football"}},
                            )
                            if res.modified_count:
                                stats["logos_added"] += 1

                stats["total_inserted"] += inserted
                stats["total_updated"] += updated
                stats["leagues_synced"] += 1
            except Exception as e:
                logger.exception(f"Errore sync league={league_name}: {e}")
                stats["leagues_failed"].append({"league": league_name, "error": str(e)[:200]})

    # Backfill slugs dopo il sync
    try:
        from services.event_slug import backfill_all_slugs
        slug_stats = await backfill_all_slugs()
        stats["slugs_updated"] = slug_stats.get("updated", 0)
    except Exception as e:
        stats["slug_error"] = str(e)

    stats["finished_at"] = datetime.now(timezone.utc).isoformat()
    stats["total_in_db"] = await db.events.count_documents({})
    stats["success"] = True

    # Salva log
    await db.sync_logs.insert_one({**stats, "log_at": datetime.now(timezone.utc), "source": "api_football"})
    return stats
