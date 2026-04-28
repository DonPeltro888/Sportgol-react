"""
Endpoint admin per sincronizzazione manuale e logs.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from routes.admin_auth import verify_admin_token
from services.matchesio_sync import sync_all_competitions
from database import db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/sync", tags=["admin-sync"])


@router.post("/matchesio")
async def manual_sync(replace_all: bool = False, _=Depends(verify_admin_token)):
    """
    Esegue sync manuale da matchesio.com.

    Query params:
    - replace_all: se True, cancella eventi importati da matchesio (preserva
                   eventi custom creati dall'admin) e re-importa.
                   Se False (default), fa upsert su matchesio_id.
    """
    try:
        stats = await sync_all_competitions(replace_all=replace_all)
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.exception("Errore durante sync manuale")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs")
async def get_sync_logs(limit: int = 10, _=Depends(verify_admin_token)):
    """Restituisce gli ultimi N log di sync."""
    logs = await db.sync_logs.find({}, {"_id": 0}).sort("log_at", -1).limit(limit).to_list(limit)
    # Convert datetime objects to iso strings
    for log in logs:
        if "log_at" in log and hasattr(log["log_at"], "isoformat"):
            log["log_at"] = log["log_at"].isoformat()
    return {"logs": logs}


@router.post("/logos")
async def manual_logos_sync(
    refresh_existing: bool = False,
    team_batch: int = 50,
    _=Depends(verify_admin_token),
):
    """
    Esegue manualmente il popolamento dei loghi (leghe + squadre) da TheSportsDB.

    Query params:
    - refresh_existing: se True, sovrascrive anche i logo già presenti.
    - team_batch: max numero di team da processare per chiamata (default 50).
                  Limit per evitare timeout (rate limit ThSportsDB = 30 req/min).
                  Per popolare TUTTI i team (~400+) richiama l'endpoint più volte.
    """
    try:
        from services.logo_fetcher import populate_all_logos
        stats = await populate_all_logos(
            refresh_existing=refresh_existing,
            team_batch=team_batch,
        )
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.exception("Errore durante logos sync")
        raise HTTPException(status_code=500, detail=str(e))
