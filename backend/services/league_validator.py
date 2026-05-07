"""
League Validator runtime — usato durante MIX sync per evitare di inserire
squadre nella lega sbagliata (es. Venezia in Serie A 2025/26).

Pipeline:
  1. Cache MongoDB della lista canonica per (league_slug, season) — 30 giorni
  2. Source A: OpenFootball (gratis, primario)
  3. Source B fallback: Perplexity Sonar (live web check)

Public API:
  await is_team_in_league(team_name, league_slug) -> bool
  await get_canonical_teams(league_slug) -> Set[str]  (norm names)
"""
import logging
import time
import json
import re
from typing import Set, Optional
from datetime import datetime, timezone, timedelta

import httpx

from database import db
from services.team_normalize import normalize_team
from services.seo_keys import get_api_key

logger = logging.getLogger(__name__)
SEASON = "2025-26"
CACHE_TTL_DAYS = 30

OPENFOOTBALL_LEAGUES = {
    "serie-a": "it.1.json",
    "serie-b": "it.2.json",
    "premier-league": "en.1.json",
    "championship": "en.2.json",
    "la-liga": "es.1.json",
    "segunda-division": "es.2.json",
    "bundesliga": "de.1.json",
    "2-bundesliga": "de.2.json",
    "ligue-1": "fr.1.json",
    "primeira-liga": "pt.1.json",
    "eredivisie": "nl.1.json",
    "champions-league": "uefa.cl.json",
    "europa-league": "uefa.el.json",
    "conference-league": "uefa.ecl.json",
}


async def _get_cache(league_slug: str) -> Optional[Set[str]]:
    doc = await db.seo_league_cache.find_one({"league_slug": league_slug, "season": SEASON})
    if not doc:
        return None
    fetched = doc.get("fetched_at")
    if fetched and isinstance(fetched, datetime):
        if datetime.now(timezone.utc) - fetched > timedelta(days=CACHE_TTL_DAYS):
            return None
    return set(doc.get("teams_norm") or [])


async def _set_cache(league_slug: str, teams_norm: Set[str], source: str) -> None:
    await db.seo_league_cache.update_one(
        {"league_slug": league_slug, "season": SEASON},
        {"$set": {
            "league_slug": league_slug,
            "season": SEASON,
            "teams_norm": list(teams_norm),
            "source": source,
            "fetched_at": datetime.now(timezone.utc),
        }},
        upsert=True,
    )


async def _from_openfootball(league_slug: str) -> Set[str]:
    path = OPENFOOTBALL_LEAGUES.get(league_slug)
    if not path:
        return set()
    url = f"https://raw.githubusercontent.com/openfootball/football.json/master/{SEASON}/{path}"
    try:
        async with httpx.AsyncClient(timeout=15) as cx:
            r = await cx.get(url)
        if r.status_code != 200:
            return set()
        d = r.json()
        out: Set[str] = set()
        for m in d.get("matches", []):
            for k in ("team1", "team2"):
                t = m.get(k)
                if isinstance(t, dict):
                    n = t.get("name") or ""
                else:
                    n = t or ""
                norm = normalize_team(n)
                if norm:
                    out.add(norm)
        return out
    except Exception as e:
        logger.warning(f"OpenFootball fetch error ({league_slug}): {e}")
        return set()


async def _from_perplexity(league_slug: str, league_pretty_name: str) -> Set[str]:
    api_key = await get_api_key("perplexity")
    if not api_key:
        return set()
    prompt = (
        f"Lista esattamente le squadre che giocano in {league_pretty_name} nella stagione {SEASON}. "
        "Restituisci SOLO un array JSON di stringhe (nomi delle squadre, niente altro). "
        "Esempio output: [\"Inter\", \"Milan\", \"Juventus\"]"
    )
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {
        "model": "sonar",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 600,
        "temperature": 0,
    }
    try:
        async with httpx.AsyncClient(timeout=30) as cx:
            r = await cx.post("https://api.perplexity.ai/chat/completions", headers=headers, json=body)
        if r.status_code not in (200, 201):
            return set()
        text = r.json()["choices"][0]["message"]["content"]
        # Extract JSON array
        m = re.search(r"\[\s*\".*?\"\s*(?:,\s*\".*?\"\s*)*\]", text, re.DOTALL)
        if not m:
            return set()
        arr = json.loads(m.group(0))
        return {normalize_team(x) for x in arr if isinstance(x, str)}
    except Exception as e:
        logger.warning(f"Perplexity fetch error ({league_slug}): {e}")
        return set()


_LEAGUE_PRETTY = {
    "serie-a": "Italian Serie A",
    "serie-b": "Italian Serie B",
    "premier-league": "English Premier League",
    "championship": "English Championship",
    "la-liga": "Spanish La Liga",
    "bundesliga": "German Bundesliga",
    "ligue-1": "French Ligue 1",
    "primeira-liga": "Portuguese Primeira Liga",
    "eredivisie": "Dutch Eredivisie",
    "champions-league": "UEFA Champions League",
    "europa-league": "UEFA Europa League",
    "conference-league": "UEFA Europa Conference League",
}


async def get_canonical_teams(league_slug: str) -> Set[str]:
    """Restituisce set di nomi normalizzati canonici per la lega.
    Usa cache 30g; in fallback Perplexity. Ritorna set vuoto se nessuna fonte risponde.
    """
    cached = await _get_cache(league_slug)
    if cached is not None:
        return cached

    teams = await _from_openfootball(league_slug)
    if teams:
        await _set_cache(league_slug, teams, "openfootball")
        return teams

    pretty = _LEAGUE_PRETTY.get(league_slug, league_slug.replace("-", " ").title())
    teams = await _from_perplexity(league_slug, pretty)
    if teams:
        await _set_cache(league_slug, teams, "perplexity")
        return teams

    return set()


async def is_team_in_league(team_name: str, league_slug: str) -> bool:
    """True se il team appartiene alla lega indicata in stagione corrente.
    Restituisce True (permissivo) se non riesce a verificare (no fonte disponibile)
    per evitare falsi negativi che bloccherebbero il sync.
    """
    if not team_name or not league_slug:
        return True
    canonical = await get_canonical_teams(league_slug)
    if not canonical:
        return True  # permissivo: nessuna fonte → non blocco
    return normalize_team(team_name) in canonical
