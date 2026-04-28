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
async def manual_sync(replace_all: bool = True, _=Depends(verify_admin_token)):
    """
    Esegue sync manuale da matchesio.com.

    Query params:
    - replace_all: se True (default), cancella tutti gli eventi e re-importa.
                   Se False, fa upsert (più conservativo).
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
