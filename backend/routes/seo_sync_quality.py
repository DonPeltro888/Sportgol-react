"""
SEO Sync Quality Dashboard — metriche real-time della qualità dei dati DB:
- Normalize counts ultime 24h/7d (events/teams/leagues)
- Health fixes ultime 24h/7d
- Top team con dati mancanti
- Trend storico duplicati per settimana
- Snapshot giornalieri (cron 02:00 UTC)
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException

from database import db
from routes.admin_auth import verify_admin_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/seo/sync-quality", tags=["seo-sync-quality"])


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


@router.get("/stats")
async def get_stats(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Metriche aggregate per il dashboard sync-quality."""
    now = datetime.now(timezone.utc)
    since_24h = (now - timedelta(hours=24)).isoformat()
    since_7d = (now - timedelta(days=7)).isoformat()

    # Counts globali
    total_events = await db.events.count_documents({})
    total_teams = await db.teams.count_documents({})
    total_leagues = await db.leagues.count_documents({})

    # Normalized markers (cumulativi)
    norm_events = await db.events.count_documents({"_normalized": True})
    norm_teams = await db.teams.count_documents({"_normalized": True})
    norm_leagues = await db.leagues.count_documents({"_normalized": True})

    # Last 24h normalize activity
    norm_24h = {
        "events": await db.events.count_documents({"_normalized_at": {"$gte": since_24h}}),
        "teams": await db.teams.count_documents({"_normalized_at": {"$gte": since_24h}}),
        "leagues": await db.leagues.count_documents({"_normalized_at": {"$gte": since_24h}}),
    }
    norm_7d = {
        "events": await db.events.count_documents({"_normalized_at": {"$gte": since_7d}}),
        "teams": await db.teams.count_documents({"_normalized_at": {"$gte": since_7d}}),
        "leagues": await db.leagues.count_documents({"_normalized_at": {"$gte": since_7d}}),
    }

    # Health fixes 24h/7d (da db.health_fixes)
    fix_24h = await db.health_fixes.count_documents({"ts": {"$gte": since_24h}})
    fix_7d = await db.health_fixes.count_documents({"ts": {"$gte": since_7d}})
    logo_replaced_7d = 0
    logo_added_7d = 0
    async for f in db.health_fixes.find({"ts": {"$gte": since_7d}}, {"_id": 0, "actions": 1}):
        for a in (f.get("actions") or []):
            if a.startswith("~logo"):
                logo_replaced_7d += 1
            elif a.startswith("+logo"):
                logo_added_7d += 1

    # Missing data ranking - top 20 team con più field mancanti
    missing_teams: List[Dict[str, Any]] = []
    async for t in db.teams.find(
        {},
        {"_id": 0, "slug": 1, "name": 1, "logo_url": 1, "stadium": 1, "city": 1, "country": 1, "league_slug": 1}
    ):
        missing = []
        if not t.get("logo_url"):
            missing.append("logo")
        if not t.get("stadium"):
            missing.append("stadium")
        if not t.get("city"):
            missing.append("city")
        if not t.get("country"):
            missing.append("country")
        if not t.get("league_slug"):
            missing.append("league")
        if missing:
            missing_teams.append({
                "slug": t.get("slug"),
                "name": t.get("name"),
                "missing": missing,
                "missing_count": len(missing),
            })
    missing_teams.sort(key=lambda x: x["missing_count"], reverse=True)

    # Trend storico (ultimi 8 snapshots se presenti)
    snapshots: List[Dict[str, Any]] = []
    async for s in db.sync_quality_snapshots.find({}, {"_id": 0}).sort("ts", -1).limit(14):
        snapshots.append(s)
    snapshots.reverse()

    # Logo coverage
    logo_proxied = await db.teams.count_documents({"logo_url": {"$regex": "^/api/seo/team-logo/"}})
    logo_external = await db.teams.count_documents({
        "logo_url": {"$exists": True, "$ne": "", "$not": {"$regex": "^/api/seo/team-logo/"}}
    })
    logo_missing = total_teams - logo_proxied - logo_external

    # SEO published counters
    events_published = await db.events.count_documents({"seo_status": "Published"})
    teams_published = await db.teams.count_documents({"seo_status": "Published"})
    leagues_published = await db.leagues.count_documents({"seo_status": "Published"})

    return {
        "ok": True,
        "scanned_at": _iso(now),
        "totals": {
            "events": total_events,
            "teams": total_teams,
            "leagues": total_leagues,
        },
        "normalize": {
            "cumulative": {"events": norm_events, "teams": norm_teams, "leagues": norm_leagues},
            "last_24h": norm_24h,
            "last_7d": norm_7d,
        },
        "health_fixes": {
            "last_24h": fix_24h,
            "last_7d": fix_7d,
            "logo_replaced_7d": logo_replaced_7d,
            "logo_added_7d": logo_added_7d,
        },
        "logo_coverage": {
            "proxied_local": logo_proxied,
            "external_url": logo_external,
            "missing": logo_missing,
            "coverage_pct": round((logo_proxied + logo_external) / max(1, total_teams) * 100, 1),
        },
        "seo_published": {
            "events": events_published,
            "teams": teams_published,
            "leagues": leagues_published,
            "total": events_published + teams_published + leagues_published,
        },
        "missing_data_top": missing_teams[:20],
        "missing_data_total": len(missing_teams),
        "trend": snapshots,
    }


@router.post("/snapshot")
async def take_snapshot(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Salva uno snapshot giornaliero per il trend storico."""
    now = datetime.now(timezone.utc)
    since_24h = (now - timedelta(hours=24)).isoformat()

    snap = {
        "ts": _iso(now),
        "date": now.date().isoformat(),
        "events_total": await db.events.count_documents({}),
        "teams_total": await db.teams.count_documents({}),
        "leagues_total": await db.leagues.count_documents({}),
        "normalized_24h_events": await db.events.count_documents({"_normalized_at": {"$gte": since_24h}}),
        "normalized_24h_teams": await db.teams.count_documents({"_normalized_at": {"$gte": since_24h}}),
        "fixes_24h": await db.health_fixes.count_documents({"ts": {"$gte": since_24h}}),
        "logo_proxied": await db.teams.count_documents({"logo_url": {"$regex": "^/api/seo/team-logo/"}}),
        "logo_missing": await db.teams.count_documents({
            "$or": [{"logo_url": {"$exists": False}}, {"logo_url": ""}, {"logo_url": None}]
        }),
        "events_published": await db.events.count_documents({"seo_status": "Published"}),
        "teams_published": await db.teams.count_documents({"seo_status": "Published"}),
    }
    await db.sync_quality_snapshots.update_one(
        {"date": snap["date"]},
        {"$set": snap},
        upsert=True,
    )
    return {"ok": True, "snapshot": snap}


@router.get("/sync-runs")
async def get_recent_sync_runs(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Lista ultimi run di sync (matchesio_sync_runs collection)."""
    runs: List[Dict[str, Any]] = []
    async for r in db.matchesio_sync_runs.find({}, {"_id": 0}).sort("started_at", -1).limit(10):
        runs.append(r)
    return {"items": runs}
