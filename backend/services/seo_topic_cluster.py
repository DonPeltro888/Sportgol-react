"""
SEO Topic Cluster / Hub-Spoke linker.

Strategia: Ogni entità SEO è un nodo in un grafo:
- LEAGUE = HUB (livello 1) — link a tutti i suoi TEAMS + EVENTS della stagione
- TEAM = HUB SECONDARIO — link al PARENT LEAGUE + tutti i suoi EVENTS upcoming
- EVENT = SPOKE — link a HOME TEAM, AWAY TEAM, PARENT LEAGUE + 3-5 EVENTS correlati

Output: per ogni entity ritorna lista di internal_links suggeriti con anchor text contestuale,
da iniettare nel campo `seo_meta.{lang}.internal_links` durante la generation pipeline.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import re

from database import db

logger = logging.getLogger(__name__)


def _slugify(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


async def _get_url_for(entity_type: str, slug: str, lang: str = "it") -> str:
    """Genera URL pubblico canonico per un'entità."""
    if entity_type == "league":
        return f"/biglietti-{slug}" if lang == "it" else f"/{lang}/biglietti-{slug}"
    if entity_type == "team":
        return f"/squadra/{slug}" if lang == "it" else f"/{lang}/squadra/{slug}"
    if entity_type == "event":
        return f"/evento/{slug}" if lang == "it" else f"/{lang}/evento/{slug}"
    return "/"


async def build_links_for_event(event: Dict[str, Any], lang: str = "it", max_related: int = 4) -> List[Dict[str, str]]:
    """Costruisce internal links per un evento: HOME, AWAY, LEAGUE, +N eventi correlati."""
    links: List[Dict[str, str]] = []
    home = event.get("home_team")
    away = event.get("away_team")
    league = event.get("league")

    # 1. Home team hub
    if home:
        team_doc = await db.teams.find_one({"name": {"$regex": f"^{re.escape(home)}$", "$options": "i"}}, {"_id": 0, "slug": 1, "name": 1})
        if team_doc:
            links.append({
                "anchor": f"Biglietti {team_doc['name']}",
                "url": await _get_url_for("team", team_doc["slug"], lang),
                "rel": "home_team",
            })
    # 2. Away team hub
    if away:
        team_doc = await db.teams.find_one({"name": {"$regex": f"^{re.escape(away)}$", "$options": "i"}}, {"_id": 0, "slug": 1, "name": 1})
        if team_doc:
            links.append({
                "anchor": f"Biglietti {team_doc['name']}",
                "url": await _get_url_for("team", team_doc["slug"], lang),
                "rel": "away_team",
            })
    # 3. Parent league
    if league:
        league_doc = await db.leagues.find_one({"name": {"$regex": f"^{re.escape(league)}$", "$options": "i"}}, {"_id": 0, "slug": 1, "name": 1})
        if league_doc:
            links.append({
                "anchor": f"Calendario {league_doc['name']}",
                "url": await _get_url_for("league", league_doc["slug"], lang),
                "rel": "parent_league",
            })
    # 4. Eventi correlati (stessa lega, prossimi N giorni, escludendo se stesso)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    self_id = event.get("slug") or event.get("id") or event.get("_id")
    rel_cursor = db.events.find(
        {"league": {"$regex": f"^{re.escape(league)}$", "$options": "i"} if league else None,
         "sort_date": {"$gte": today_str},
         "slug": {"$ne": self_id}},
        {"_id": 0, "slug": 1, "home_team": 1, "away_team": 1, "sort_date": 1},
    ).sort("sort_date", 1).limit(max_related)
    async for rel in rel_cursor:
        if not rel.get("slug"):
            continue
        anchor = f"{rel.get('home_team','?')} vs {rel.get('away_team','?')}"
        links.append({
            "anchor": anchor,
            "url": await _get_url_for("event", rel["slug"], lang),
            "rel": "related_event",
        })
    return links


async def build_links_for_team(team: Dict[str, Any], lang: str = "it", max_events: int = 5) -> List[Dict[str, str]]:
    """Internal links team: parent league + N eventi prossimi del team."""
    links: List[Dict[str, str]] = []
    league_slug = team.get("league_slug")
    team_name = team.get("name")
    if league_slug:
        lg = await db.leagues.find_one({"slug": league_slug}, {"_id": 0, "slug": 1, "name": 1})
        if lg:
            links.append({
                "anchor": f"Calendario {lg['name']}",
                "url": await _get_url_for("league", lg["slug"], lang),
                "rel": "parent_league",
            })
    if team_name:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        team_re = f"^{re.escape(team_name)}$"
        ev_cursor = db.events.find(
            {"$or": [{"home_team": {"$regex": team_re, "$options": "i"}},
                     {"away_team": {"$regex": team_re, "$options": "i"}}],
             "sort_date": {"$gte": today_str}},
            {"_id": 0, "slug": 1, "home_team": 1, "away_team": 1, "sort_date": 1},
        ).sort("sort_date", 1).limit(max_events)
        async for ev in ev_cursor:
            if not ev.get("slug"):
                continue
            links.append({
                "anchor": f"{ev.get('home_team','?')} vs {ev.get('away_team','?')}",
                "url": await _get_url_for("event", ev["slug"], lang),
                "rel": "team_event",
            })
    return links


async def build_links_for_league(league: Dict[str, Any], lang: str = "it", max_teams: int = 8, max_events: int = 6) -> List[Dict[str, str]]:
    """Internal links league: tutti i teams del league + N eventi prossimi."""
    links: List[Dict[str, str]] = []
    league_slug = league.get("slug")
    if not league_slug:
        return links
    teams_cursor = db.teams.find(
        {"league_slug": league_slug}, {"_id": 0, "slug": 1, "name": 1}
    ).sort("name", 1).limit(max_teams)
    async for t in teams_cursor:
        links.append({
            "anchor": f"{t['name']}",
            "url": await _get_url_for("team", t["slug"], lang),
            "rel": "child_team",
        })
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    league_name = league.get("name") or ""
    ev_cursor = db.events.find(
        {"league": {"$regex": f"^{re.escape(league_name)}$", "$options": "i"},
         "sort_date": {"$gte": today_str}},
        {"_id": 0, "slug": 1, "home_team": 1, "away_team": 1, "sort_date": 1},
    ).sort("sort_date", 1).limit(max_events)
    async for ev in ev_cursor:
        if not ev.get("slug"):
            continue
        links.append({
            "anchor": f"{ev.get('home_team','?')} vs {ev.get('away_team','?')}",
            "url": await _get_url_for("event", ev["slug"], lang),
            "rel": "child_event",
        })
    return links


async def build_links(entity_type: str, entity: Dict[str, Any], lang: str = "it") -> List[Dict[str, str]]:
    if entity_type == "event":
        return await build_links_for_event(entity, lang)
    if entity_type == "team":
        return await build_links_for_team(entity, lang)
    if entity_type == "league":
        return await build_links_for_league(entity, lang)
    return []


async def cluster_overview() -> Dict[str, Any]:
    """Stats globali del cluster: per ogni league quanti teams + events; per ogni team quanti events."""
    total_leagues = await db.leagues.count_documents({"active": True})
    total_teams = await db.teams.count_documents({})
    total_events_future = await db.events.count_documents(
        {"sort_date": {"$gte": datetime.now(timezone.utc).strftime("%Y-%m-%d")}}
    )

    # Top league hubs
    pipe_leagues = [
        {"$match": {"active": True}},
        {"$lookup": {"from": "teams", "localField": "slug", "foreignField": "league_slug", "as": "teams"}},
        {"$project": {
            "_id": 0, "slug": 1, "name": 1, "country": 1,
            "team_count": {"$size": "$teams"},
        }},
        {"$sort": {"team_count": -1}},
        {"$limit": 30},
    ]
    league_hubs = await db.leagues.aggregate(pipe_leagues).to_list(None)

    # Add events per league (separato per evitare lookup costoso)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for lg in league_hubs:
        ev_count = await db.events.count_documents({
            "league": {"$regex": f"^{re.escape(lg.get('name',''))}$", "$options": "i"},
            "sort_date": {"$gte": today_str},
        })
        lg["future_events"] = ev_count

    return {
        "total_leagues": total_leagues,
        "total_teams": total_teams,
        "total_events_future": total_events_future,
        "league_hubs": league_hubs,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
