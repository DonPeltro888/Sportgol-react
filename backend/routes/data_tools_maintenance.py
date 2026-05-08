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
