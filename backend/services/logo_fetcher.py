"""
Logo fetcher service - usa TheSportsDB API gratuita per recuperare:
- Loghi delle leghe (badge/logo)
- Loghi delle squadre (badge)

API: https://www.thesportsdb.com/api/v1/json/3/

Rate limit: 30 requests/minute (gratis). Cachiamo i risultati in DB
per evitare chiamate ripetute. Usiamo throttle di 2.1s tra le chiamate.
"""
import logging
import time
import requests
from typing import Optional, Dict, List
from database import db

logger = logging.getLogger(__name__)

THESPORTSDB_BASE = "https://www.thesportsdb.com/api/v1/json/3"
USER_AGENT = "Mozilla/5.0 GoleventsBot/1.0"
RATE_LIMIT_DELAY = 2.1  # secondi tra ogni request (30/min limit)

# Mapping curato: slug interno → query string per TheSportsDB
LEAGUE_LOGO_MAP = {
    "serie-a":              ("Italy", "Italian Serie A"),
    "premier-league":       ("England", "English Premier League"),
    "la-liga":              ("Spain", "Spanish La Liga"),
    "bundesliga":           ("Germany", "German Bundesliga"),
    "ligue-1":              ("France", "French Ligue 1"),
    "liga-portugal":        ("Portugal", "Portuguese Primeira Liga"),
    "super-lig":            ("Turkey", "Turkish Super Lig"),
    "eredivisie":           ("Netherlands", "Dutch Eredivisie"),
    "jupiler-pro-league":   ("Belgium", "Belgian Pro League"),
    "championship":         ("England", "English League Championship"),
    "2-bundesliga":         ("Germany", "German 2. Bundesliga"),
    "ligue-2":              ("France", "French Ligue 2"),
    "mls":                  ("USA", "American Major League Soccer"),
    "liga-mx":              ("Mexico", "Mexican Primera Division"),
    "j1-league":            ("Japan", "Japanese J1 League"),
    "coppa-italia":         ("Italy", "Coppa Italia"),
    "copa-del-rey":         ("Spain", "Spanish Copa del Rey"),
    "fa-cup":               ("England", "English FA Cup"),
    "dfb-pokal":            ("Germany", "German DFB Pokal"),
    "coupe-de-france":      ("France", "French Coupe de France"),
    "knvb-beker":           ("Netherlands", "Dutch KNVB Beker"),
    "champions-league":     ("Europe", "UEFA Champions League"),
    "europa-league":        ("Europe", "UEFA Europa League"),
    "conference-league":    ("Europe", "UEFA Europa Conference League"),
    "uefa-nations-league":  ("Europe", "UEFA Nations League"),
    "fifa-world-cup-2026":  ("World", "World Cup"),
    "fifa-club-world-cup":  ("World", "FIFA Club World Cup"),
    "euro-championship":    ("Europe", "UEFA Euro Championship"),
    "copa-america":         ("South America", "Copa America"),
    "africa-cup-of-nations": ("Africa", "Africa Cup of Nations"),
    "asian-cup":            ("Asia", "AFC Asian Cup"),
    "copa-libertadores":    ("South America", "CONMEBOL Libertadores"),
    "afc-champions-league": ("Asia", "AFC Champions League"),
}


def _http_get(url: str) -> Optional[Dict]:
    """GET con rate-limiting e gestione errori. Ritorna dict JSON o None."""
    time.sleep(RATE_LIMIT_DELAY)  # Throttle: 30 req/min
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code == 429:
            logger.warning("logo_fetcher: rate-limited (429), aspetto 60s e riprovo")
            time.sleep(60)
            r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        if r.status_code == 200 and r.content:
            try:
                return r.json()
            except Exception:
                return None
    except Exception as e:
        logger.warning(f"logo_fetcher HTTP error: {e}")
    return None


def fetch_league_logo(slug: str) -> Optional[str]:
    """
    Cerca il logo della lega su TheSportsDB.
    Strategy:
    1. Usa LEAGUE_LOGO_MAP per ottenere country + nome ufficiale
    2. Cerca tramite searchleagues.php
    3. Fallback: search_all_leagues.php?c={country}
    """
    mapping = LEAGUE_LOGO_MAP.get(slug)
    if not mapping:
        return None
    country, league_name = mapping

    # Tentativo 1: searchleagues per nome
    data = _http_get(f"{THESPORTSDB_BASE}/searchleagues.php?l={league_name.replace(' ', '%20')}")
    if data:
        leagues = data.get("countries") or data.get("leagues") or []
        for league in leagues:
            badge = league.get("strBadge") or league.get("strLogo")
            if badge:
                return badge

    # Tentativo 2: cerca per country
    data = _http_get(f"{THESPORTSDB_BASE}/search_all_leagues.php?c={country.replace(' ', '%20')}&s=Soccer")
    if data:
        leagues = data.get("countries") or data.get("leagues") or []
        for league in leagues:
            if league.get("strLeague", "").lower() == league_name.lower():
                badge = league.get("strBadge") or league.get("strLogo")
                if badge:
                    return badge

    logger.info(f"logo_fetcher: nessun logo trovato per league {slug}")
    return None


def fetch_team_logo(team_name: str) -> Optional[str]:
    """
    Cerca il badge del team su TheSportsDB.
    Restituisce URL del logo o None.
    """
    if not team_name or team_name in ("TBD", "TBA"):
        return None

    # Prova prima nome esatto
    encoded = team_name.replace(" ", "%20").replace("&", "%26")
    data = _http_get(f"{THESPORTSDB_BASE}/searchteams.php?t={encoded}")
    if not data:
        return None

    teams = data.get("teams") or []
    if not teams:
        return None

    # Filtra solo squadre di calcio (Sport: Soccer)
    soccer_teams = [t for t in teams if (t.get("strSport") or "").lower() == "soccer"]
    if soccer_teams:
        for t in soccer_teams:
            badge = t.get("strBadge")
            if badge:
                return badge

    # Fallback: prima squadra qualunque
    for t in teams:
        badge = t.get("strBadge")
        if badge:
            return badge

    return None


async def populate_league_logos() -> Dict:
    """
    Per ogni lega in db.leagues senza logo, fetcha da TheSportsDB e salva.
    Restituisce stats.
    """
    stats = {"updated": 0, "skipped": 0, "not_found": 0}

    cursor = db.leagues.find({})
    async for league in cursor:
        if league.get("logo_url"):
            stats["skipped"] += 1
            continue

        slug = league.get("slug")
        logo = fetch_league_logo(slug)
        if logo:
            await db.leagues.update_one(
                {"_id": league["_id"]},
                {"$set": {"logo_url": logo}}
            )
            stats["updated"] += 1
            logger.info(f"logo_fetcher: aggiornato logo per lega {slug} -> {logo}")
        else:
            stats["not_found"] += 1

    return stats


async def populate_team_logos(refresh_existing: bool = False, batch_limit: int = 50) -> Dict:
    """
    Estrae i nomi delle squadre dagli eventi e crea/aggiorna db.teams con logo.

    Args:
        refresh_existing: se True, rifecta logo anche per teams che già lo hanno
        batch_limit: max numero di team da processare in una sola chiamata
                     (per evitare lunghi blocking call e rate limits)
    """
    stats = {"created": 0, "updated_logo": 0, "skipped": 0, "not_found": 0,
             "remaining": 0, "batch_limit": batch_limit}

    # Estrae tutti i nomi unici di home/away dagli eventi
    pipeline = [
        {"$project": {"teams": [
            {"name": "$home_team", "league": "$league"},
            {"name": "$away_team", "league": "$league"},
        ]}},
        {"$unwind": "$teams"},
        {"$group": {
            "_id": "$teams.name",
            "leagues": {"$addToSet": "$teams.league"},
        }},
    ]
    teams_cursor = db.events.aggregate(pipeline)
    unique_teams: List[Dict] = await teams_cursor.to_list(length=10000)

    logger.info(f"logo_fetcher: trovati {len(unique_teams)} team unici negli eventi")

    # Ordina per priorità: team con almeno 1 lega popolare prima
    POPULAR_LEAGUES = {
        "SERIE A", "PREMIER LEAGUE", "LA LIGA", "BUNDESLIGA", "LIGUE 1",
        "CHAMPIONS LEAGUE", "EUROPA LEAGUE", "FIFA WORLD CUP 2026"
    }
    def _sort_key(e):
        leagues = e.get("leagues", [])
        return (-int(any(l in POPULAR_LEAGUES for l in leagues)), e["_id"])
    unique_teams.sort(key=_sort_key)

    processed = 0
    for entry in unique_teams:
        if processed >= batch_limit:
            stats["remaining"] = len(unique_teams) - processed
            break

        team_name = entry["_id"]
        leagues = entry.get("leagues", [])

        if not team_name or team_name in ("TBD", "TBA"):
            continue

        existing = await db.teams.find_one({"name": team_name})

        if existing and existing.get("logo_url") and not refresh_existing:
            stats["skipped"] += 1
            continue

        logo = fetch_team_logo(team_name)
        processed += 1

        if not logo:
            stats["not_found"] += 1
            continue

        team_slug = team_name.lower().replace(" ", "-").replace("'", "").replace("&", "and")
        team_slug = "".join(c for c in team_slug if c.isalnum() or c == "-")

        if existing:
            await db.teams.update_one(
                {"_id": existing["_id"]},
                {"$set": {"logo_url": logo}}
            )
            stats["updated_logo"] += 1
        else:
            # Determina la primary league (prima della lista)
            primary_league = leagues[0] if leagues else None
            league_doc = await db.leagues.find_one(
                {"name": {"$regex": f"^{primary_league}$", "$options": "i"}}
            ) if primary_league else None
            league_slug = league_doc.get("slug") if league_doc else None

            await db.teams.insert_one({
                "name": team_name,
                "slug": team_slug,
                "logo_url": logo,
                "league_slug": league_slug,
                "active": True,
                "auto_created": True,
                "order": 999,
            })
            stats["created"] += 1
            logger.info(f"logo_fetcher: creato team {team_name} con logo")

    return stats


async def populate_all_logos(refresh_existing: bool = False, team_batch: int = 50) -> Dict:
    """Esegue il popolamento di logo leghe + team in sequenza."""
    leagues_stats = await populate_league_logos()
    teams_stats = await populate_team_logos(refresh_existing=refresh_existing, batch_limit=team_batch)
    return {
        "leagues": leagues_stats,
        "teams": teams_stats,
    }
