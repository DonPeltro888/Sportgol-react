"""
DB Normalize layer — applica normalize_team/normalize_league SU OGNI INSERT/UPSERT
di events/teams/leagues per evitare duplicati con varianti di nome.

Usage (al posto di db.events.insert_one(doc)):
    await insert_event(doc)
    await upsert_event({"slug": ev["slug"]}, ev)
    await insert_team(doc)
    await upsert_team({"slug": t["slug"]}, t)
    await insert_league(doc)
    await upsert_league({"slug": lg["slug"]}, lg)

Tutti i doc passati ricevono `_normalized: True` per marker.
Il backstop scheduler (services/scheduler.py) può poi normalizzare retroactively
tutti i doc con `_normalized != True`.
"""
import logging
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any, Dict

from database import db
from services.team_normalize import normalize_team, normalize_league

logger = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    s = unicodedata.normalize("NFKD", text or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:80]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Event ────────────────────────────────────────────────────────────────

def normalize_event_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalizza in-place i campi di un event doc:
    - home_team / away_team → canonical
    - league → canonical
    Conserva i raw originali in home_team_raw/away_team_raw/league_raw.
    Aggiunge _normalized=True + _normalized_at.
    """
    if not isinstance(doc, dict):
        return doc

    h_raw = (doc.get("home_team") or "").strip()
    a_raw = (doc.get("away_team") or "").strip()
    l_raw = (doc.get("league") or "").strip()

    if h_raw:
        h_norm = normalize_team(h_raw)
        if h_norm and h_norm != h_raw:
            doc["home_team_raw"] = doc.get("home_team_raw") or h_raw
            doc["home_team"] = h_norm.title() if h_norm.islower() else h_norm
    if a_raw:
        a_norm = normalize_team(a_raw)
        if a_norm and a_norm != a_raw:
            doc["away_team_raw"] = doc.get("away_team_raw") or a_raw
            doc["away_team"] = a_norm.title() if a_norm.islower() else a_norm
    if l_raw:
        l_norm = normalize_league(l_raw)
        if l_norm and l_norm != l_raw:
            doc["league_raw"] = doc.get("league_raw") or l_raw
            doc["league"] = l_norm.title() if l_norm.islower() else l_norm

    # Recompute title/slug on normalized names if missing
    if not doc.get("title") and doc.get("home_team") and doc.get("away_team"):
        doc["title"] = f"{doc['home_team']} vs {doc['away_team']}"
    if not doc.get("slug") and doc.get("home_team") and doc.get("away_team"):
        date_part = ""
        sd = doc.get("sort_date") or doc.get("date") or ""
        if isinstance(sd, str) and len(sd) >= 10:
            date_part = "-" + sd[:10]
        elif isinstance(sd, datetime):
            date_part = "-" + sd.isoformat()[:10]
        doc["slug"] = _slugify(f"{doc['home_team']}-vs-{doc['away_team']}{date_part}")

    doc["_normalized"] = True
    doc["_normalized_at"] = _now_iso()
    return doc


async def insert_event(doc: Dict[str, Any]):
    return await db.events.insert_one(normalize_event_doc(doc))


async def upsert_event(filter_q: Dict[str, Any], doc: Dict[str, Any], **kw):
    norm = normalize_event_doc(dict(doc))
    return await db.events.update_one(filter_q, {"$set": norm}, upsert=True, **kw)


# ─── Team ─────────────────────────────────────────────────────────────────

def normalize_team_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(doc, dict):
        return doc
    name_raw = (doc.get("name") or "").strip()
    if name_raw:
        norm = normalize_team(name_raw)
        if norm and norm != name_raw:
            doc["name_raw"] = doc.get("name_raw") or name_raw
            doc["name"] = norm.title() if norm.islower() else norm
    if doc.get("name") and not doc.get("slug"):
        doc["slug"] = _slugify(doc["name"])
    league_raw = (doc.get("league") or "").strip()
    if league_raw:
        ln = normalize_league(league_raw)
        if ln and ln != league_raw:
            doc["league_raw"] = doc.get("league_raw") or league_raw
            doc["league"] = ln.title() if ln.islower() else ln
    if doc.get("league") and not doc.get("league_slug"):
        doc["league_slug"] = _slugify(doc["league"])
    doc["_normalized"] = True
    doc["_normalized_at"] = _now_iso()
    return doc


async def insert_team(doc: Dict[str, Any]):
    return await db.teams.insert_one(normalize_team_doc(doc))


async def upsert_team(filter_q: Dict[str, Any], doc: Dict[str, Any], **kw):
    norm = normalize_team_doc(dict(doc))
    return await db.teams.update_one(filter_q, {"$set": norm}, upsert=True, **kw)


# ─── League ───────────────────────────────────────────────────────────────

def normalize_league_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(doc, dict):
        return doc
    name_raw = (doc.get("name") or "").strip()
    if name_raw:
        ln = normalize_league(name_raw)
        if ln and ln != name_raw:
            doc["name_raw"] = doc.get("name_raw") or name_raw
            doc["name"] = ln.title() if ln.islower() else ln
    if doc.get("name") and not doc.get("slug"):
        doc["slug"] = _slugify(doc["name"])
    doc["_normalized"] = True
    doc["_normalized_at"] = _now_iso()
    return doc


async def insert_league(doc: Dict[str, Any]):
    return await db.leagues.insert_one(normalize_league_doc(doc))


async def upsert_league(filter_q: Dict[str, Any], doc: Dict[str, Any], **kw):
    norm = normalize_league_doc(dict(doc))
    return await db.leagues.update_one(filter_q, {"$set": norm}, upsert=True, **kw)


# ─── Backstop: normalizza retroactively qualsiasi doc con _normalized != True ──

async def backstop_normalize_all(limit: int = 5000) -> Dict[str, int]:
    """Esegue la normalizzazione su record che non hanno il marker."""
    counters = {"events": 0, "teams": 0, "leagues": 0}
    # Events
    async for d in db.events.find({"_normalized": {"$ne": True}}, {"_id": 1, "home_team": 1, "away_team": 1, "league": 1}).limit(limit):
        upd = normalize_event_doc({k: v for k, v in d.items() if k != "_id"})
        await db.events.update_one({"_id": d["_id"]}, {"$set": upd})
        counters["events"] += 1
    # Teams
    async for d in db.teams.find({"_normalized": {"$ne": True}}, {"_id": 1, "name": 1, "league": 1, "slug": 1}).limit(limit):
        upd = normalize_team_doc({k: v for k, v in d.items() if k != "_id"})
        await db.teams.update_one({"_id": d["_id"]}, {"$set": upd})
        counters["teams"] += 1
    # Leagues
    async for d in db.leagues.find({"_normalized": {"$ne": True}}, {"_id": 1, "name": 1, "slug": 1}).limit(limit):
        upd = normalize_league_doc({k: v for k, v in d.items() if k != "_id"})
        await db.leagues.update_one({"_id": d["_id"]}, {"$set": upd})
        counters["leagues"] += 1
    return counters
