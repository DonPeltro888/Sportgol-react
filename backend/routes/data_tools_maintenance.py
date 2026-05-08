"""
Data Tools Maintenance routes — DB hygiene operations (NON SEO).

Spostate qui da seo_admin.py per coerenza architetturale: il modulo SEO
deve restare portabile, queste sono operazioni golevents-specific su DB.

Endpoints:
- POST /api/data-tools/maintenance/dedup           → dedup events+teams+leagues
- POST /api/data-tools/maintenance/validate-leagues → valida composizione vs fonti ufficiali
"""
import logging
import sys
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, Depends

from database import db
from routes.admin_auth import verify_admin_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/data-tools/maintenance", tags=["data-tools-maintenance"])


@router.post("/dedup")
async def run_dedup(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Esegue dedup events+teams+leagues. Da usare dopo un MIX sync multi-fonte."""
    sys.path.insert(0, "/app/backend")
    from scripts.dedup_entities import dedup_events, dedup_teams, dedup_leagues  # type: ignore

    res_e = await dedup_events(db, dry_run=False)
    res_t = await dedup_teams(db, dry_run=False)
    res_l = await dedup_leagues(db, dry_run=False)
    return {
        "ok": True,
        "events": res_e,
        "teams": res_t,
        "leagues": res_l,
        "ran_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/validate-leagues")
async def run_validate_leagues(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Valida composizione leghe contro OpenFootball + Perplexity. Squadre obsolete archiviate."""
    sys.path.insert(0, "/app/backend")
    from scripts.validate_leagues import validate_league, OPENFOOTBALL_LEAGUES  # type: ignore

    out: Dict[str, Any] = {"results": []}
    for lg in OPENFOOTBALL_LEAGUES:
        try:
            r = await validate_league(db, lg, dry_run=False)
            out["results"].append(r)
        except Exception as e:
            out["results"].append({"league": lg, "error": str(e)[:200]})
    out["ran_at"] = datetime.now(timezone.utc).isoformat()
    return out



@router.post("/resolve-conflicts")
async def run_resolve_conflicts(
    dry_run: bool = False,
    window_hours: int = 12,
    days_forward: int = 365,
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """
    Risolve conflitti di scheduling: nessun team può giocare 2 partite nello stesso giorno
    (window ±window_hours). Usa la trust hierarchy (matchesio > apifootball > espn > ... > ai_perplexity)
    per decidere quale evento mantenere; gli altri vengono marcati `_dropped_conflict=True`
    (nascosti dalle pagine pubbliche ma conservati per audit).
    """
    from services.event_conflict_resolver import resolve_all_conflicts, canonicalize_league_names
    canon = await canonicalize_league_names(dry_run=dry_run)
    res = await resolve_all_conflicts(window_hours=window_hours, dry_run=dry_run, days_forward=days_forward)
    return {
        "ok": True,
        "league_canonicalize": canon,
        "conflict_resolve": res,
        "ran_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/conflicts/list")
async def list_dropped_conflicts(
    limit: int = 200,
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """Lista degli eventi marcati come conflittuali (per audit / undo manuale)."""
    rows = await db.events.find(
        {"_dropped_conflict": True},
        {"_id": 1, "home_team": 1, "away_team": 1, "sort_date": 1, "league": 1,
         "source": 1, "slug": 1, "_dropped_reason": 1, "_dropped_at": 1},
    ).sort("_dropped_at", -1).limit(limit).to_list(limit)
    for r in rows:
        r["_id"] = str(r["_id"])
    return {"total": len(rows), "rows": rows}


@router.post("/conflicts/restore/{event_id}")
async def restore_conflict_event(
    event_id: str,
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """Rimuove il flag `_dropped_conflict` da un evento (override manuale)."""
    from bson import ObjectId
    from bson.errors import InvalidId
    try:
        oid = ObjectId(event_id)
    except (InvalidId, TypeError):
        return {"ok": False, "error": "invalid_event_id"}
    res = await db.events.update_one(
        {"_id": oid},
        {"$unset": {"_dropped_conflict": "", "_dropped_reason": "", "_dropped_at": ""}},
    )
    return {"ok": True, "modified": res.modified_count}
