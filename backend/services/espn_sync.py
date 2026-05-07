"""
ESPN public API sync — fonte primaria gratis senza auth.
Endpoint: site.api.espn.com/apis/site/v2/sports/soccer/{espn_slug}/scoreboard?dates=YYYYMMDD-YYYYMMDD

Vantaggi vs matchesio.com (ora 404):
- Copre tutte le competizioni mondiali (top leghe + coppe + WC + nazionali)
- No API key, no rate-limit aggressivo (in pratica ~30 req/min senza problemi)
- JSON pulito e affidabile
- Aggiornato live (segna anche risultati / status partite)

NOTE: Match ESPN id stabile → upsert su `espn_id` per evitare duplicati.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple, Optional

import httpx
from database import db
from services.matchesio_sync import (
    normalize_team, fmt_ita_date, ensure_league_in_db,
    STANDARD_SECTORS, STADIUM_IMAGES, BIG_CLUBS,
)

logger = logging.getLogger(__name__)

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Mapping ESPN slug → (db_slug, nome lega DB, country, type, order)
# ESPN slug = identificatore competizione nell'URL ESPN
COMPETITIONS: List[Tuple[str, str, str, str, str, int]] = [
    # ===== TOP 7 LEAGUES =====
    ("ita.1",                "serie-a",            "SERIE A",            "Italy",         "league",  1),
    ("eng.1",                "premier-league",     "PREMIER LEAGUE",     "England",       "league",  2),
    ("esp.1",                "la-liga",            "LA LIGA",            "Spain",         "league",  3),
    ("ger.1",                "bundesliga",         "BUNDESLIGA",         "Germany",       "league",  4),
    ("fra.1",                "ligue-1",            "LIGUE 1",            "France",        "league",  5),
    ("por.1",                "liga-portugal",      "LIGA PORTUGAL",      "Portugal",      "league",  6),
    ("tur.1",                "super-lig",          "SUPER LIG",          "Turkey",        "league",  7),
    # ===== ALTRE LEGHE EUROPEE =====
    ("ned.1",                "eredivisie",         "EREDIVISIE",         "Netherlands",   "league",  8),
    ("bel.1",                "jupiler-pro-league", "JUPILER PRO LEAGUE", "Belgium",       "league",  9),
    ("eng.2",                "championship",       "CHAMPIONSHIP",       "England",       "league", 20),
    ("ger.2",                "2-bundesliga",       "2. BUNDESLIGA",      "Germany",       "league", 21),
    ("fra.2",                "ligue-2",            "LIGUE 2",            "France",        "league", 22),
    # ===== LEGHE EXTRA-EUROPA =====
    ("usa.1",                "mls",                "MLS",                "USA",           "league", 30),
    ("mex.1",                "liga-mx",            "LIGA MX",            "Mexico",        "league", 31),
    ("jpn.1",                "j1-league",          "J1 LEAGUE",          "Japan",         "league", 32),
    # ===== COPPE NAZIONALI =====
    ("ita.coppa_italia",     "coppa-italia",       "COPPA ITALIA",       "Italy",         "cup",    50),
    ("esp.copa_del_rey",     "copa-del-rey",       "COPA DEL REY",       "Spain",         "cup",    51),
    ("eng.fa",               "fa-cup",             "FA CUP",             "England",       "cup",    52),
    ("ger.dfb_pokal",        "dfb-pokal",          "DFB POKAL",          "Germany",       "cup",    53),
    ("fra.coupe_de_france",  "coupe-de-france",    "COUPE DE FRANCE",    "France",        "cup",    54),
    ("ned.knvb_beker",       "knvb-beker",         "KNVB BEKER",         "Netherlands",   "cup",    55),
    # ===== COPPE EUROPEE =====
    ("uefa.champions",       "champions-league",   "CHAMPIONS LEAGUE",   "Europe",        "cup",    70),
    ("uefa.europa",          "europa-league",      "EUROPA LEAGUE",      "Europe",        "cup",    71),
    ("uefa.europa.conf",     "conference-league",  "CONFERENCE LEAGUE",  "Europe",        "cup",    72),
    ("uefa.nations_league",  "uefa-nations-league", "UEFA NATIONS LEAGUE","Europe",       "cup",    73),
    # ===== INTERNAZIONALI =====
    ("fifa.world",           "fifa-world-cup-2026", "FIFA WORLD CUP 2026", "USA / Canada / Mexico", "cup", 90),
    ("fifa.cwc",             "fifa-club-world-cup", "FIFA CLUB WORLD CUP", "International", "cup",  91),
    ("uefa.euro",            "euro-championship",   "EURO CHAMPIONSHIP",   "Europe",        "cup",  92),
    ("conmebol.america",     "copa-america",        "COPA AMERICA",        "South America", "cup",  93),
    ("conmebol.libertadores","copa-libertadores",   "COPA LIBERTADORES",   "South America", "cup",  96),
    ("afc.champions",        "afc-champions-league", "AFC CHAMPIONS LEAGUE", "Asia",       "cup",   97),
]


def _date_chunks(days_forward: int = 90, chunk_days: int = 30) -> List[str]:
    """Genera range YYYYMMDD-YYYYMMDD per coprire i prossimi `days_forward` giorni
    in chunk da `chunk_days`. ESPN limita range troppo larghi."""
    out = []
    today = datetime.now(timezone.utc).date()
    for i in range(0, days_forward, chunk_days):
        start = today + timedelta(days=i)
        end = today + timedelta(days=min(i + chunk_days - 1, days_forward - 1))
        out.append(f"{start.strftime('%Y%m%d')}-{end.strftime('%Y%m%d')}")
    return out


async def _fetch_espn_competition(client: httpx.AsyncClient, espn_slug: str, days_forward: int = 90) -> List[Dict]:
    """Scarica events ESPN per una competizione su tutta la finestra futura."""
    out: List[Dict] = []
    seen_ids = set()
    for date_range in _date_chunks(days_forward):
        url = f"{ESPN_BASE}/{espn_slug}/scoreboard"
        try:
            r = await client.get(url, params={"dates": date_range, "limit": 100},
                                 headers={"User-Agent": USER_AGENT}, timeout=20)
            if r.status_code != 200:
                logger.warning(f"espn: HTTP {r.status_code} {espn_slug} {date_range}")
                continue
            d = r.json()
            for ev in (d.get("events") or []):
                ev_id = ev.get("id")
                if ev_id and ev_id not in seen_ids:
                    seen_ids.add(ev_id)
                    out.append(ev)
        except Exception as e:
            logger.error(f"espn: errore fetch {espn_slug} {date_range}: {e}")
    return out


def _parse_espn_event(ev: Dict) -> Optional[Dict]:
    """Estrae i campi standard da un event ESPN raw."""
    try:
        ev_id = ev.get("id")
        date_iso = ev.get("date") or ""  # "2026-05-05T19:00Z"
        comps = ev.get("competitions") or []
        if not comps or not date_iso:
            return None
        comp = comps[0]
        competitors = comp.get("competitors") or []
        if len(competitors) < 2:
            return None

        home = next((c for c in competitors if c.get("homeAway") == "home"), competitors[0])
        away = next((c for c in competitors if c.get("homeAway") == "away"), competitors[1])
        home_team = (home.get("team") or {}).get("displayName") or "TBD"
        away_team = (away.get("team") or {}).get("displayName") or "TBD"

        venue = comp.get("venue") or {}
        stadium = venue.get("fullName") or "TBA"
        addr = venue.get("address") or {}
        city = addr.get("city") or "TBD"
        country = addr.get("country") or ""

        # Parse date as UTC
        try:
            dt = datetime.strptime(date_iso, "%Y-%m-%dT%H:%MZ")
        except ValueError:
            dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00"))
            dt = dt.replace(tzinfo=None)

        date_str = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")

        # Round / matchday (per coppe ESPN espone "season.slug" e "type.text" come round)
        round_str = (ev.get("season") or {}).get("type", {}).get("name") if isinstance((ev.get("season") or {}).get("type"), dict) else None
        # In ESPN, comp.notes[0].headline a volte contiene "Group A - Round 1"
        notes = comp.get("notes") or []
        if notes and isinstance(notes, list) and notes[0].get("headline"):
            round_str = notes[0]["headline"]

        return {
            "espn_id": str(ev_id),
            "home": home_team,
            "away": away_team,
            "date": date_str,
            "time": time_str,
            "stadium": stadium,
            "city": city,
            "country": country,
            "round": round_str,
            "raw_status": ((comp.get("status") or {}).get("type") or {}).get("name"),
        }
    except Exception as e:
        logger.warning(f"espn parse error: {e}")
        return None


async def sync_via_espn(days_forward: int = 90) -> Dict:
    """Sync principale ESPN. Upsert su `espn_id` (chiave stabile)."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stats = {
        "source": "espn",
        "total_inserted": 0,
        "total_updated": 0,
        "leagues_created": [],
        "leagues_empty": [],
        "per_league": {},
        "errors": [],
        "sample_inserted": [],
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    sem = asyncio.Semaphore(5)
    async with httpx.AsyncClient(timeout=30) as client:
        async def fetch_one(comp):
            espn_slug, db_slug, league_name, country, league_type, order = comp
            async with sem:
                raw = await _fetch_espn_competition(client, espn_slug, days_forward)
            return (espn_slug, db_slug, league_name, country, league_type, order, raw)

        results = await asyncio.gather(*[fetch_one(c) for c in COMPETITIONS], return_exceptions=True)

    img_idx = 0
    for r in results:
        if isinstance(r, Exception):
            stats["errors"].append(f"fetch error: {r}")
            continue
        espn_slug, db_slug, league_name, country, league_type, order, raw_events = r
        try:
            league_status = await ensure_league_in_db(db_slug, league_name, country, league_type, order)
            if league_status["created"]:
                stats["leagues_created"].append({"name": league_name, "slug": db_slug, "type": league_type})

            league_count = 0
            for raw in raw_events:
                p = _parse_espn_event(raw)
                if not p:
                    continue
                # Solo eventi futuri
                if p["date"] < today_str:
                    continue

                home = normalize_team(p["home"])
                away = normalize_team(p["away"])
                if not home or not away or home == "TBD" or away == "TBD":
                    # Conserviamo TBD solo per coppe (es. finali da definire)
                    if league_type != "cup":
                        continue

                try:
                    sort_dt = datetime.fromisoformat(f"{p['date']}T{p['time']}:00")
                    sort_date = sort_dt.strftime("%Y-%m-%dT%H:%M:%S")
                except Exception:
                    sort_date = f"{p['date']}T20:00:00"

                title = f"{home} vs {away}"
                if p.get("round") and league_type == "cup":
                    title += f" - {p['round']}"

                featured = home in BIG_CLUBS or away in BIG_CLUBS

                event_doc = {
                    "title": title,
                    "home_team": home,
                    "away_team": away,
                    "league": league_name,
                    "stadium": p["stadium"] or "TBA",
                    "location": p["city"] or "TBD",
                    "country": p["country"] or country,
                    "date": fmt_ita_date(p["date"]),
                    "time": p["time"],
                    "sort_date": sort_date,
                    "categories": [home.upper(), away.upper()],
                    "ticket_categories": [s.copy() for s in STANDARD_SECTORS],
                    "available_tickets": 30000 if featured else 15000,
                    "image": STADIUM_IMAGES[img_idx % len(STADIUM_IMAGES)],
                    "imageUrl": STADIUM_IMAGES[img_idx % len(STADIUM_IMAGES)],
                    "seo_sectors": ", ".join(s["name"] for s in STANDARD_SECTORS),
                    "has_stadium_map": False,
                    "stadium_map_type": None,
                    "featured": featured,
                    "espn_id": p["espn_id"],
                    "source": "espn",
                    "updated_at": datetime.now(timezone.utc),
                }

                from services.db_normalize import normalize_event_doc
                # Upsert su espn_id (chiave stabile)
                result = await db.events.update_one(
                    {"espn_id": p["espn_id"]},
                    {"$set": normalize_event_doc(event_doc),
                     "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
                    upsert=True,
                )
                if result.upserted_id:
                    stats["total_inserted"] += 1
                    if len(stats["sample_inserted"]) < 10:
                        stats["sample_inserted"].append({"title": title, "league": league_name, "date": event_doc["date"]})
                elif result.modified_count > 0:
                    stats["total_updated"] += 1

                league_count += 1
                img_idx += 1

            stats["per_league"][league_name] = league_count
            if league_count == 0:
                stats["leagues_empty"].append({"league": league_name, "espn_slug": espn_slug})
            logger.info(f"espn: {league_name} -> {league_count} eventi futuri")
        except Exception as e:
            err_msg = f"{espn_slug}: {str(e)}"
            stats["errors"].append(err_msg)
            logger.exception(f"espn sync errore: {err_msg}")

    stats["finished_at"] = datetime.now(timezone.utc).isoformat()
    stats["total_in_db"] = await db.events.count_documents({})

    # Slug backfill
    try:
        from services.event_slug import backfill_all_slugs
        slug_stats = await backfill_all_slugs()
        stats["slugs_updated"] = slug_stats.get("updated", 0)
    except Exception as e:
        stats["slug_backfill_error"] = str(e)

    await db.sync_logs.insert_one({**stats, "log_at": datetime.now(timezone.utc)})
    return stats
