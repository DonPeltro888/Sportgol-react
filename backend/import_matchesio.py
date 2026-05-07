"""
Import REALE da matchesio.com - JSON pubblico con date ufficiali.
Sostituisce tutti gli eventi nel DB con dati ufficiali.
Mantiene i 7 settori standard senza prezzo.
"""
import asyncio
import os
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']

BASE_URL = "https://www.matchesio.com/it/competition"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Mappa slug matchesio -> nome lega nel DB
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

# 7 settori standard (no prezzo)
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

# Squadre considerate "featured" (top clubs)
BIG_CLUBS = {
    "Inter", "AC Milan", "Milan", "Juventus", "AS Roma", "Roma", "Napoli", "Lazio",
    "Atalanta", "Fiorentina", "Real Madrid", "FC Barcelona", "Barcelona",
    "Atlético Madrid", "Atletico Madrid", "Sevilla", "Athletic Bilbao",
    "Valencia", "Real Betis", "Real Sociedad",
    "Manchester City", "Manchester United", "Liverpool", "Chelsea", "Arsenal",
    "Tottenham Hotspur", "Tottenham", "Newcastle United",
    "Bayern München", "Bayern Munich", "Bayern Munchen", "Borussia Dortmund",
    "Bayer 04 Leverkusen", "Bayer Leverkusen", "RB Leipzig",
    "Paris Saint-Germain", "PSG", "Olympique de Marseille", "Marseille",
    "Olympique Lyonnais", "Lyon", "AS Monaco", "Monaco",
    "SL Benfica", "Benfica", "FC Porto", "Porto", "Sporting CP", "Sporting Clube",
    "Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor",
    # National teams
    "Argentina", "Brazil", "France", "Spain", "Germany", "England",
    "Portugal", "Netherlands", "Italy", "Belgium", "USA",
    "Mexico", "Croatia", "Canada", "Japan",
}


def fmt_ita_date(date_str: str) -> str:
    """Convert '2026-05-03' to 'Domenica, 3 Maggio 2026'."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{ITA_DAYS[dt.weekday()]}, {dt.day} {ITA_MONTHS[dt.month]} {dt.year}"


def normalize_team(name: str) -> str:
    """Normalize team name (remove club prefixes, capitalize)."""
    if not name:
        return ""
    name = name.strip()
    # Capitalize first letter of each word but preserve common patterns
    if name == name.lower() or name == name.upper():
        name = " ".join(w.capitalize() for w in name.split())
    return name


def fetch_competition(slug: str):
    """Download JSON from matchesio for given competition slug."""
    url = f"{BASE_URL}/{slug}/export/json/"
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
        if r.status_code != 200:
            print(f"  [WARN] HTTP {r.status_code} for {slug}")
            return []
        return r.json()
    except Exception as e:
        print(f"  [ERROR] {slug}: {e}")
        return []


async def run_import():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    print("=" * 70)
    print("IMPORT REALE DA matchesio.com")
    print("=" * 70)

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_str = today.strftime("%Y-%m-%d")

    # 1. Cancella tutti gli eventi esistenti per ripartire pulito
    deleted = await db.events.delete_many({})
    print(f"\nCancellati eventi esistenti: {deleted.deleted_count}")

    # 2. Importa per ogni competizione
    total_inserted = 0
    img_idx = 0

    for slug, league_name, country, league_type in COMPETITIONS:
        print(f"\nFetching: {slug} -> {league_name}")
        matches = fetch_competition(slug)
        print(f"  Ricevuti {len(matches)} match dal sito")

        # Filtra solo partite future (data >= oggi)
        future_matches = [
            m for m in matches
            if m.get("date", "") >= today_str
        ]
        print(f"  Match futuri: {len(future_matches)}")

        for m in future_matches:
            home = normalize_team(m.get("homeTeam", "TBD"))
            away = normalize_team(m.get("awayTeam", "TBD"))
            date_str = m.get("date", "")
            time_str = m.get("time", "20:00")
            city = m.get("city", "TBD") or "TBD"
            stadium = m.get("stadium", "TBA") or "TBA"
            matchday = m.get("matchday")

            if not date_str or not home or not away:
                continue

            # Costruisci sort_date ISO
            try:
                sort_dt = datetime.fromisoformat(f"{date_str}T{time_str}:00")
                sort_date = sort_dt.strftime("%Y-%m-%dT%H:%M:%S")
            except Exception:
                sort_date = f"{date_str}T20:00:00"

            # Titolo
            title = f"{home} vs {away}"
            # Per cup, aggiungi suffisso turno se presente
            round_str = m.get("round") or m.get("stage")
            if round_str and league_type == "cup":
                title += f" - {round_str}"

            # featured?
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
                "matchesio_id": m.get("id"),
                "matchday": matchday,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            from services.db_normalize import insert_event
            await insert_event(event_doc)
            total_inserted += 1
            img_idx += 1

    # 3. Stats finali
    total = await db.events.count_documents({})
    print(f"\n{'=' * 70}")
    print(f"IMPORT COMPLETATO")
    print(f"  Eventi totali: {total}")
    print(f"  Eventi inseriti: {total_inserted}")
    print('=' * 70)

    # Mostra esempi per ogni lega
    print("\nDistribuzione per lega:")
    cursor = db.events.aggregate([
        {"$group": {"_id": "$league", "count": {"$sum": 1}, "first_date": {"$min": "$sort_date"}}},
        {"$sort": {"count": -1}}
    ])
    async for row in cursor:
        print(f"  {row['_id']}: {row['count']} match (prima: {row['first_date']})")

    client.close()


if __name__ == "__main__":
    asyncio.run(run_import())
