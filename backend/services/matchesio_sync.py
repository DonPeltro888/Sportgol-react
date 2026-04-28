"""
Modulo riusabile per import eventi da matchesio.com.
Usato da:
- routes/sync.py (endpoint admin manuale)
- scheduler (cron job automatico)
- import_matchesio.py (CLI/seed)
"""
import logging
from datetime import datetime, timezone
from typing import Dict

import requests
from database import db

logger = logging.getLogger(__name__)

BASE_URL = "https://www.matchesio.com/it/competition"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

COMPETITIONS = [
    ("serie-a-it",            "SERIE A",            "Italy",         "league"),
    ("premier-league-gb-eng", "PREMIER LEAGUE",     "England",       "league"),
    ("la-liga-es",            "LA LIGA",            "Spain",         "league"),
    ("bundesliga-de",         "BUNDESLIGA",         "Germany",       "league"),
    ("ligue-1-fr",            "LIGUE 1",            "France",        "league"),
    ("primeira-liga-pt",      "LIGA PORTUGAL",      "Portugal",      "league"),
    ("super-lig-tr",          "SUPER LIG",          "Turkey",        "league"),
    ("uefa-champions-league", "CHAMPIONS LEAGUE",   "Europe",        "cup"),
    ("coppa-italia-it",       "COPPA ITALIA",       "Italy",         "cup"),
    ("copa-del-rey-es",       "COPA DEL REY",       "Spain",         "cup"),
    ("fa-cup-gb-eng",         "FA CUP",             "England",       "cup"),
    ("dfb-pokal-de",          "DFB POKAL",          "Germany",       "cup"),
    ("world-cup",             "FIFA WORLD CUP 2026", "USA / Canada / Mexico", "cup"),
]

STANDARD_SECTORS = [
    {"name": "Cat 1 - Lower Central",     "available": True, "notes": ""},
    {"name": "Cat 1 - Middle Central",    "available": True, "notes": ""},
    {"name": "Cat 1 - Normal",            "available": True, "notes": ""},
    {"name": "Cat 2 - Long Upper",        "available": True, "notes": ""},
    {"name": "Cat 2 - Short Lower",       "available": True, "notes": ""},
    {"name": "Cat 3 - Short Side Middle", "available": True, "notes": ""},
    {"name": "Cat 4 - Short Upper",       "available": True, "notes": ""},
]

ITA_DAYS = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
ITA_MONTHS = ["", "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
              "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]

STADIUM_IMAGES = [
    "https://images.unsplash.com/photo-1574629810360-7efbbe195018",
    "https://images.unsplash.com/photo-1522778119026-d647f0596c20",
    "https://images.unsplash.com/photo-1599158150601-1417ebbaafdd",
    "https://images.unsplash.com/photo-1629217855633-79a6925d6c47",
    "https://images.unsplash.com/photo-1489944440615-453fc2b6a9a9",
    "https://images.unsplash.com/photo-1592336563179-5a95288563c9",
    "https://images.unsplash.com/photo-1560969961-bc5368188cb9",
    "https://images.unsplash.com/photo-1705593813682-033ee2991df6",
]

# Casi speciali per nomi che vanno mantenuti specifici (case-sensitive)
SPECIAL_CASE_NAMES = {
    "usa":            "USA",
    "uk":             "UK",
    "psg":            "PSG",
    "rb leipzig":     "RB Leipzig",
    "ac milan":       "AC Milan",
    "as roma":        "AS Roma",
    "as monaco":      "AS Monaco",
    "ss lazio":       "SS Lazio",
    "sl benfica":     "SL Benfica",
    "fc porto":       "FC Porto",
    "fc barcelona":   "FC Barcelona",
    "vfl wolfsburg":  "VfL Wolfsburg",
    "vfb stuttgart":  "VfB Stuttgart",
    "tsg hoffenheim": "TSG Hoffenheim",
    "1899 hoffenheim": "Hoffenheim",
    "como":           "Como",
    "bosnia & herzegovina": "Bosnia & Herzegovina",
    "côte d'ivoire":  "Côte d'Ivoire",
    "cote d'ivoire":  "Côte d'Ivoire",
    "south africa":   "South Africa",
    "south korea":    "South Korea",
    "saudi arabia":   "Saudi Arabia",
    "czech republic": "Czech Republic",
    "north macedonia": "North Macedonia",
    "cape verde":     "Cape Verde",
    "ivory coast":    "Côte d'Ivoire",
}

BIG_CLUBS = {
    "Inter", "AC Milan", "Juventus", "AS Roma", "Napoli", "SS Lazio",
    "Atalanta", "Fiorentina", "Real Madrid", "FC Barcelona",
    "Atlético Madrid", "Sevilla", "Athletic Bilbao", "Valencia", "Real Betis",
    "Real Sociedad", "Manchester City", "Manchester United", "Liverpool",
    "Chelsea", "Arsenal", "Tottenham Hotspur", "Newcastle United",
    "Bayern München", "Borussia Dortmund", "Bayer 04 Leverkusen", "RB Leipzig",
    "Paris Saint-Germain", "PSG", "Olympique de Marseille", "Olympique Lyonnais",
    "AS Monaco", "SL Benfica", "FC Porto", "Sporting CP",
    "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor",
    "Argentina", "Brazil", "France", "Spain", "Germany", "England",
    "Portugal", "Netherlands", "Italy", "Belgium", "USA", "Mexico",
    "Croatia", "Canada", "Japan",
}


def normalize_team(name: str) -> str:
    """Normalizza un nome squadra: gestisce SPECIAL_CASE + Title Case generale."""
    if not name:
        return ""
    cleaned = name.strip()
    lower_key = cleaned.lower()
    if lower_key in SPECIAL_CASE_NAMES:
        return SPECIAL_CASE_NAMES[lower_key]
    # Title case generico, ma preserva apostrofi e parole "vs", "&"
    parts = cleaned.split()
    out = []
    for p in parts:
        if p.lower() in ("vs", "&"):
            out.append(p.lower() if p == "vs" else p)
            continue
        # Capitalizza la prima lettera, mantieni il resto se già misto
        if p and (p == p.lower() or p == p.upper()):
            out.append(p.capitalize())
        else:
            out.append(p)
    return " ".join(out)


def fmt_ita_date(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{ITA_DAYS[dt.weekday()]}, {dt.day} {ITA_MONTHS[dt.month]} {dt.year}"


def fetch_competition_json(slug: str):
    """Scarica il JSON ufficiale di una competizione."""
    url = f"{BASE_URL}/{slug}/export/json/"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
        if r.status_code != 200:
            logger.warning(f"matchesio: HTTP {r.status_code} for slug={slug}")
            return []
        return r.json()
    except Exception as e:
        logger.error(f"matchesio: errore fetch slug={slug}: {e}")
        return []


async def sync_all_competitions(replace_all: bool = True) -> Dict:
    """
    Sincronizza tutti gli eventi da matchesio.com.

    Args:
        replace_all: se True, cancella tutti gli eventi esistenti prima dell'import.
                     Se False, fa upsert su matchesio_id (più sicuro per cron).

    Returns:
        dict con stats: total_inserted, total_updated, per_league {nome: count}
    """
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stats = {
        "total_inserted": 0,
        "total_updated": 0,
        "total_deleted_past": 0,
        "per_league": {},
        "errors": [],
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    if replace_all:
        deleted = await db.events.delete_many({})
        stats["total_deleted_past"] = deleted.deleted_count
        logger.info(f"sync: cancellati {deleted.deleted_count} eventi esistenti")

    img_idx = 0
    for slug, league_name, country, league_type in COMPETITIONS:
        try:
            matches = fetch_competition_json(slug)
            future_matches = [m for m in matches if m.get("date", "") >= today_str]
            league_count = 0

            for m in future_matches:
                home = normalize_team(m.get("homeTeam", "TBD"))
                away = normalize_team(m.get("awayTeam", "TBD"))
                date_str = m.get("date", "")
                time_str = m.get("time", "20:00")
                city = m.get("city", "TBD") or "TBD"
                stadium = m.get("stadium", "TBA") or "TBA"
                matchday = m.get("matchday")
                matchesio_id = m.get("id")

                if not date_str or not home or not away:
                    continue

                try:
                    sort_dt = datetime.fromisoformat(f"{date_str}T{time_str}:00")
                    sort_date = sort_dt.strftime("%Y-%m-%dT%H:%M:%S")
                except Exception:
                    sort_date = f"{date_str}T20:00:00"

                title = f"{home} vs {away}"
                round_str = m.get("round") or m.get("stage")
                if round_str and league_type == "cup":
                    title += f" - {round_str}"

                featured = home in BIG_CLUBS or away in BIG_CLUBS

                event_doc = {
                    "title": title,
                    "home_team": home,
                    "away_team": away,
                    "league": league_name,
                    "stadium": stadium,
                    "location": city,
                    "country": country,
                    "date": fmt_ita_date(date_str),
                    "time": time_str,
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
                    "matchesio_id": matchesio_id,
                    "matchday": matchday,
                    "updated_at": datetime.now(timezone.utc),
                }

                if replace_all:
                    event_doc["created_at"] = datetime.now(timezone.utc)
                    await db.events.insert_one(event_doc)
                    stats["total_inserted"] += 1
                else:
                    # Upsert su matchesio_id se presente
                    if matchesio_id:
                        result = await db.events.update_one(
                            {"matchesio_id": matchesio_id},
                            {"$set": event_doc, "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
                            upsert=True,
                        )
                        if result.upserted_id:
                            stats["total_inserted"] += 1
                        elif result.modified_count > 0:
                            stats["total_updated"] += 1
                    else:
                        event_doc["created_at"] = datetime.now(timezone.utc)
                        await db.events.insert_one(event_doc)
                        stats["total_inserted"] += 1

                league_count += 1
                img_idx += 1

            stats["per_league"][league_name] = league_count
            logger.info(f"sync: {league_name} -> {league_count} eventi futuri")

        except Exception as e:
            err_msg = f"{slug}: {str(e)}"
            stats["errors"].append(err_msg)
            logger.exception(f"sync errore: {err_msg}")

    # Cancella eventi passati (anche in modalità upsert)
    if not replace_all:
        deleted = await db.events.delete_many({"sort_date": {"$lt": today_str}})
        stats["total_deleted_past"] = deleted.deleted_count

    stats["finished_at"] = datetime.now(timezone.utc).isoformat()
    stats["total_in_db"] = await db.events.count_documents({})

    # Salva log dell'esecuzione
    await db.sync_logs.insert_one({**stats, "log_at": datetime.now(timezone.utc)})

    return stats
