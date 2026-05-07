"""
AI Gap Detector — usa Perplexity Sonar Pro (real-time web search) per trovare
match mancanti dal DB e auto-inserirli con cross-validation.

Pipeline:
1. Per ogni lega configurata, chiede a Perplexity la lista UFFICIALE dei prossimi
   match dei prossimi N giorni con web search live.
2. Confronta con db.events: usa rapidfuzz per matching home+away+date_window.
3. Per ogni match mancante, lo inserisce in db.events con source='ai_perplexity'
   e flag _multi_source_verified=False (solo 1 fonte per ora).
4. Logga in db.sync_logs con source='ai_gap_detector'.

Costi: chiama Perplexity ~30 volte (una per lega) ogni notte = ~$0.15/giorno con Sonar Pro.
"""
import json
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

import httpx
from rapidfuzz import fuzz

from database import db
from services.seo_keys import get_api_key
from services.matchesio_sync import (
    normalize_team, fmt_ita_date, ensure_league_in_db,
    STANDARD_SECTORS, STADIUM_IMAGES, BIG_CLUBS,
)

logger = logging.getLogger(__name__)

# Subset delle leghe da controllare (TOP + coppe internazionali con maggior gap-risk)
# Stesso schema di espn_sync (db_slug, nome lega DB, country, type, order)
LEAGUES_TO_VERIFY: List[Tuple[str, str, str, str]] = [
    # (db_slug, nome lega DB, country, type)
    ("serie-a",            "Serie A",            "Italy",         "league"),
    ("premier-league",     "Premier League",     "England",       "league"),
    ("la-liga",            "La Liga",            "Spain",         "league"),
    ("bundesliga",         "Bundesliga",         "Germany",       "league"),
    ("ligue-1",            "Ligue 1",            "France",        "league"),
    ("liga-portugal",      "Liga Portugal",      "Portugal",      "league"),
    ("super-lig",          "Super Lig",          "Turkey",        "league"),
    ("eredivisie",         "Eredivisie",         "Netherlands",   "league"),
    ("champions-league",   "Champions League",   "Europe",        "cup"),
    ("europa-league",      "Europa League",      "Europe",        "cup"),
    ("conference-league",  "Conference League",  "Europe",        "cup"),
    ("fifa-world-cup-2026", "FIFA World Cup 2026", "USA / Canada / Mexico", "cup"),
    ("coppa-italia",       "Coppa Italia",       "Italy",         "cup"),
    ("copa-del-rey",       "Copa del Rey",       "Spain",         "cup"),
    ("fa-cup",             "FA Cup",             "England",       "cup"),
    ("dfb-pokal",          "DFB Pokal",          "Germany",       "cup"),
    ("mls",                "MLS",                "USA",           "league"),
]


async def _ask_perplexity_for_fixtures(
    league_name: str, days_window: int = 30
) -> List[Dict]:
    """Chiede a Perplexity la lista dei prossimi match ufficiali della lega.
    Ritorna una lista di {home, away, date (YYYY-MM-DD), time (HH:MM), stadium, city}.
    """
    api_key = await get_api_key("perplexity")
    if not api_key:
        logger.warning("AI Gap Detector: no Perplexity API key configured")
        return []

    today = datetime.now(timezone.utc).date()
    end = today + timedelta(days=days_window)

    prompt = (
        f"Search official sources (UEFA, FIFA, league official websites, Wikipedia) "
        f"for the OFFICIAL list of all '{league_name}' football matches "
        f"scheduled between {today.isoformat()} and {end.isoformat()}. "
        f"Include ALL fixtures: regular season, knockout rounds, finals, qualifiers. "
        f"Return ONLY a valid JSON array (no markdown, no explanation), each item with EXACTLY these keys: "
        f'{{"home":"team1 name","away":"team2 name","date":"YYYY-MM-DD","time":"HH:MM",'
        f'"stadium":"stadium name","city":"city","round":"matchday or round name"}}. '
        f"Use 24-hour time format UTC. If no matches scheduled, return []. "
        f"DO NOT include past matches. DO NOT include matches with fully unknown teams (TBD vs TBD)."
    )

    body = {
        "model": "sonar-pro",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000,
        "temperature": 0.0,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=90) as cx:
            r = await cx.post("https://api.perplexity.ai/chat/completions", headers=headers, json=body)
        if r.status_code not in (200, 201):
            logger.warning(f"AI Gap Detector: Perplexity HTTP {r.status_code} for {league_name}: {r.text[:200]}")
            return []
        text = r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.error(f"AI Gap Detector: Perplexity error for {league_name}: {e}")
        return []

    # Estrae JSON array dalla risposta (può essere wrappato in ```json ... ```)
    m = re.search(r"\[\s*\{.*?\}\s*\]", text, re.DOTALL)
    if not m:
        # nessun JSON array trovato → 0 match
        return []
    raw = m.group(0)
    try:
        items = json.loads(raw)
        return [it for it in items if isinstance(it, dict) and it.get("home") and it.get("away") and it.get("date")]
    except json.JSONDecodeError as e:
        logger.warning(f"AI Gap Detector: JSON decode error for {league_name}: {e}")
        return []


def _is_match_in_db_list(ai_match: Dict, db_matches: List[Dict], threshold: int = 80) -> bool:
    """Determina se ai_match è già presente in db_matches usando fuzzy matching su (home+away+date)."""
    ai_home = normalize_team(ai_match.get("home", "")).lower()
    ai_away = normalize_team(ai_match.get("away", "")).lower()
    ai_date = (ai_match.get("date") or "")[:10]
    if not ai_home or not ai_away or not ai_date:
        return False
    for db_m in db_matches:
        db_home = (db_m.get("home_team") or "").lower()
        db_away = (db_m.get("away_team") or "").lower()
        db_date = (db_m.get("sort_date") or "")[:10]
        if not db_home or not db_away:
            continue
        # Stessa data ± 1 giorno (tolleranza fuso) e fuzzy match nomi
        try:
            d1 = datetime.fromisoformat(ai_date)
            d2 = datetime.fromisoformat(db_date)
            if abs((d1 - d2).days) > 1:
                continue
        except Exception:
            if ai_date != db_date:
                continue
        # Try direct + swapped (Perplexity può confondere home/away)
        score_direct = (fuzz.ratio(ai_home, db_home) + fuzz.ratio(ai_away, db_away)) / 2
        score_swap = (fuzz.ratio(ai_home, db_away) + fuzz.ratio(ai_away, db_home)) / 2
        if max(score_direct, score_swap) >= threshold:
            return True
    return False


async def _insert_ai_match(ai_match: Dict, league_name: str, country: str, league_type: str, img_idx: int) -> bool:
    """Inserisce un match AI-discovered in db.events. Ritorna True se inserito."""
    home = normalize_team(ai_match.get("home", "TBD"))
    away = normalize_team(ai_match.get("away", "TBD"))
    date_str = (ai_match.get("date") or "")[:10]
    time_str = ai_match.get("time") or "20:00"
    if len(time_str) > 5:
        time_str = time_str[:5]
    stadium = ai_match.get("stadium") or "TBA"
    city = ai_match.get("city") or "TBD"
    round_str = ai_match.get("round") or ""

    if not date_str or not home or not away:
        return False

    try:
        sort_dt = datetime.fromisoformat(f"{date_str}T{time_str}:00")
        sort_date = sort_dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        sort_date = f"{date_str}T20:00:00"

    title = f"{home} vs {away}"
    if round_str and league_type == "cup":
        title += f" - {round_str}"

    featured = home in BIG_CLUBS or away in BIG_CLUBS

    # Compute deterministic AI ID per upsert idempotente
    ai_id = f"ai-{league_name.lower().replace(' ', '-')}-{date_str}-{home.lower().replace(' ', '-')}-{away.lower().replace(' ', '-')}"

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
        "ai_match_id": ai_id,
        "source": "ai_perplexity",
        "_multi_source_verified": False,
        "updated_at": datetime.now(timezone.utc),
    }

    from services.db_normalize import normalize_event_doc
    result = await db.events.update_one(
        {"ai_match_id": ai_id},
        {"$set": normalize_event_doc(event_doc),
         "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return bool(result.upserted_id)


async def detect_and_fill_gaps_one_league(
    db_slug: str, league_name: str, country: str, league_type: str,
    days_window: int = 30, auto_insert: bool = True,
) -> Dict:
    """Rileva e (opzionalmente) inserisce gap per una singola lega."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    end_str = (datetime.now(timezone.utc) + timedelta(days=days_window)).strftime("%Y-%m-%d")

    # 1. Snapshot DB events nel range (case-insensitive su league per gestire "Coppa Italia" vs "COPPA ITALIA")
    import re as _re
    league_re = f"^{_re.escape(league_name)}$"
    db_matches = await db.events.find(
        {"league": {"$regex": league_re, "$options": "i"},
         "sort_date": {"$gte": today_str, "$lte": f"{end_str}T23:59:59"}},
        {"_id": 0, "home_team": 1, "away_team": 1, "sort_date": 1},
    ).to_list(500)

    # 2. AI fetch
    ai_matches = await _ask_perplexity_for_fixtures(league_name, days_window)

    # 3. Diff
    missing = [m for m in ai_matches if not _is_match_in_db_list(m, db_matches)]

    # 4. Insert (se richiesto)
    inserted = 0
    if auto_insert and missing:
        await ensure_league_in_db(db_slug, league_name.upper(), country, league_type, 99)
        for i, m in enumerate(missing):
            try:
                ok = await _insert_ai_match(m, league_name, country, league_type, i)
                if ok:
                    inserted += 1
            except Exception as e:
                logger.warning(f"AI Gap Detector insert error: {e}")

    return {
        "league_slug": db_slug,
        "league_name": league_name,
        "db_count": len(db_matches),
        "ai_count": len(ai_matches),
        "missing_count": len(missing),
        "inserted": inserted,
        "missing_sample": [
            {"home": m.get("home"), "away": m.get("away"), "date": m.get("date")}
            for m in missing[:5]
        ],
    }


async def detect_and_fill_gaps_all(days_window: int = 30, auto_insert: bool = True) -> Dict:
    """Esegue il check su TUTTE le leghe attive presenti nel DB (non una lista hardcoded).
    Questo è il flusso "DB-driven AI verification": legge le leghe dal DB
    (db.leagues active=True) e per ognuna chiede a Perplexity di verificare
    quali match mancano rispetto alle fonti ufficiali.
    """
    stats = {
        "source": "ai_gap_detector",
        "leagues_checked": 0,
        "leagues_with_gaps": 0,
        "total_missing": 0,
        "total_inserted": 0,
        "per_league": [],
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    # 1. Leggi TUTTE le leghe attive dal DB (DB-driven)
    leagues_cursor = db.leagues.find(
        {"active": True},
        {"_id": 0, "slug": 1, "name": 1, "country": 1, "type": 1},
    ).sort("order", 1)
    leagues_list = await leagues_cursor.to_list(length=200)

    if not leagues_list:
        # Fallback: usa la lista hardcoded
        leagues_list = [
            {"slug": s, "name": n, "country": c, "type": t}
            for s, n, c, t in LEAGUES_TO_VERIFY
        ]

    logger.info(f"AI Gap Detector: starting DB-driven check on {len(leagues_list)} active leagues")

    for lg in leagues_list:
        db_slug = lg.get("slug")
        league_name = lg.get("name") or ""
        # Normalizza il nome (DB ha sia "Serie A" che "SERIE A")
        league_name_clean = league_name.title() if league_name.isupper() else league_name
        country = lg.get("country") or ""
        league_type = lg.get("type") or "league"

        if not db_slug or not league_name_clean:
            continue

        try:
            res = await detect_and_fill_gaps_one_league(
                db_slug, league_name_clean, country, league_type, days_window, auto_insert
            )
            stats["leagues_checked"] += 1
            stats["total_missing"] += res["missing_count"]
            stats["total_inserted"] += res["inserted"]
            if res["missing_count"] > 0:
                stats["leagues_with_gaps"] += 1
            stats["per_league"].append(res)
            logger.info(
                f"AI Gap Detector [{league_name_clean}]: db={res['db_count']}, ai={res['ai_count']}, "
                f"missing={res['missing_count']}, inserted={res['inserted']}"
            )
        except Exception as e:
            logger.exception(f"AI Gap Detector errore lega {league_name_clean}: {e}")

    stats["finished_at"] = datetime.now(timezone.utc).isoformat()
    await db.sync_logs.insert_one({**stats, "log_at": datetime.now(timezone.utc)})
    return stats
