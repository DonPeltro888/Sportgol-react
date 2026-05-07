"""
Data Recovery routes — pannello admin per multi-source resync on-demand.
Espone:
- GET  /api/data-tools/data-recovery/sources-status  → stato fonti per lega
- POST /api/data-tools/data-recovery/run-espn        → sync ESPN globale
- POST /api/data-tools/data-recovery/run-ai-gap      → AI gap detector (Perplexity)
- POST /api/data-tools/data-recovery/run-league/{slug}  → resync mirato per lega (ESPN+AI)
- GET  /api/data-tools/data-recovery/logs            → ultimi sync_logs di tutte le fonti
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query

from database import db
from routes.admin_auth import verify_admin_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/data-tools/data-recovery", tags=["data-tools-recovery"])


@router.get("/sources-status")
async def sources_status(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Per ogni lega: numero eventi futuri totali + per fonte (espn/matchesio/openfootball/thesportsdb/ai_perplexity)."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    pipeline = [
        {"$match": {"sort_date": {"$gte": today_str}}},
        {"$group": {
            "_id": {"league": "$league", "source": {"$ifNull": ["$source", "matchesio"]}},
            "count": {"$sum": 1},
        }},
        {"$sort": {"_id.league": 1}},
    ]
    rows = await db.events.aggregate(pipeline).to_list(None)

    by_league: Dict[str, Dict[str, int]] = {}
    for r in rows:
        league = r["_id"]["league"] or "Unknown"
        source = r["_id"]["source"] or "matchesio"
        by_league.setdefault(league, {})[source] = r["count"]

    leagues_doc = await db.leagues.find({"active": True}, {"_id": 0, "slug": 1, "name": 1, "type": 1, "country": 1}).to_list(200)
    league_lookup = {lg["name"]: lg for lg in leagues_doc}

    rows_out: List[Dict[str, Any]] = []
    for name, sources_dict in sorted(by_league.items()):
        total = sum(sources_dict.values())
        meta = league_lookup.get(name, {})
        # match by uppercase fallback
        if not meta:
            for ln, lm in league_lookup.items():
                if ln.upper() == name.upper():
                    meta = lm
                    break
        rows_out.append({
            "league": name,
            "slug": meta.get("slug", ""),
            "type": meta.get("type", ""),
            "country": meta.get("country", ""),
            "total_future": total,
            "by_source": sources_dict,
            "is_at_risk": total < 3,  # < 3 eventi futuri = a rischio
        })

    return {
        "rows": rows_out,
        "total_leagues": len(rows_out),
        "at_risk_count": sum(1 for r in rows_out if r["is_at_risk"]),
        "ts": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/run-espn")
async def run_espn_sync(
    days_forward: int = Query(90, ge=7, le=365),
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """Sync ESPN globale per tutte le competizioni configurate."""
    from services.espn_sync import sync_via_espn
    stats = await sync_via_espn(days_forward=days_forward)
    return stats


@router.post("/run-openfootball")
async def run_openfootball_sync(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Sync OpenFootball GitHub."""
    try:
        from services.openfootball_sync import sync_via_openfootball
        return await sync_via_openfootball()
    except Exception as e:
        raise HTTPException(500, f"openfootball error: {e}")


@router.post("/run-thesportsdb")
async def run_thesportsdb_sync(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Sync TheSportsDB."""
    try:
        from services.thesportsdb_sync import sync_via_thesportsdb
        return await sync_via_thesportsdb()
    except Exception as e:
        raise HTTPException(500, f"thesportsdb error: {e}")


@router.post("/run-ai-gap")
async def run_ai_gap_detector(
    days_window: int = Query(30, ge=7, le=90),
    auto_insert: bool = Query(True),
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """AI Gap Detector con Perplexity Sonar Pro."""
    from services.ai_gap_detector import detect_and_fill_gaps_all
    stats = await detect_and_fill_gaps_all(days_window=days_window, auto_insert=auto_insert)
    return stats


@router.post("/run-league/{league_slug}")
async def run_league_resync(
    league_slug: str,
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """Resync mirato per una lega specifica (ESPN + AI Gap Detector)."""
    league = await db.leagues.find_one({"slug": league_slug}, {"_id": 0, "name": 1, "country": 1, "type": 1})
    if not league:
        raise HTTPException(404, f"League {league_slug} not found")

    out: Dict[str, Any] = {"league_slug": league_slug, "results": {}}

    # 1. ESPN: filtra COMPETITIONS sul slug richiesto (best-effort: matching db_slug)
    try:
        from services.espn_sync import sync_via_espn, COMPETITIONS as ESPN_COMPS
        target_comp = next((c for c in ESPN_COMPS if c[1] == league_slug), None)
        if target_comp:
            # Re-execute giusto questa competizione richiamando sync_via_espn con override interna
            # → semplificazione: chiamiamo full sync ma il resto è idempotente
            stats = await sync_via_espn(days_forward=90)
            out["results"]["espn"] = {
                "inserted": stats.get("per_league", {}).get(target_comp[2], 0),
                "ok": True,
            }
        else:
            out["results"]["espn"] = {"skipped": "league not in ESPN COMPETITIONS map"}
    except Exception as e:
        out["results"]["espn"] = {"error": str(e)}

    # 2. AI Gap Detector mirato
    try:
        from services.ai_gap_detector import detect_and_fill_gaps_one_league
        ai_res = await detect_and_fill_gaps_one_league(
            league_slug, league["name"], league["country"], league.get("type", "league"),
            days_window=30, auto_insert=True,
        )
        out["results"]["ai_perplexity"] = ai_res
    except Exception as e:
        out["results"]["ai_perplexity"] = {"error": str(e)}

    out["finished_at"] = datetime.now(timezone.utc).isoformat()
    return out


@router.get("/logs")
async def get_recovery_logs(
    limit: int = Query(20, ge=1, le=100),
    source: str = Query(None),
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """Ultimi sync_logs raggruppati per fonte."""
    flt: Dict[str, Any] = {}
    if source:
        flt["source"] = source
    cursor = db.sync_logs.find(flt, {"_id": 0}).sort("log_at", -1).limit(limit)
    items = []
    async for d in cursor:
        # Riassunto leggibile
        items.append({
            "source": d.get("source", "?"),
            "started_at": d.get("started_at"),
            "finished_at": d.get("finished_at"),
            "log_at": (d.get("log_at").isoformat() if isinstance(d.get("log_at"), datetime) else d.get("log_at")),
            "total_inserted": d.get("total_inserted", 0),
            "total_updated": d.get("total_updated", 0),
            "leagues_empty": len(d.get("leagues_empty", []) or []),
            "errors": (d.get("errors") or [])[:5],
            "leagues_checked": d.get("leagues_checked"),
            "leagues_with_gaps": d.get("leagues_with_gaps"),
            "total_missing": d.get("total_missing"),
        })
    return {"items": items, "count": len(items)}
