"""
Endpoint admin per sincronizzazione manuale e logs.
"""
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
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


@router.post("/team-logo/{team_id}")
async def refresh_single_team_logo(team_id: str, _=Depends(verify_admin_token)):
    """Refresh del logo di una singola squadra da TheSportsDB."""
    try:
        team = await db.teams.find_one({"_id": ObjectId(team_id)})
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        import httpx
        from services.logo_fetcher import fetch_team_logo
        async with httpx.AsyncClient() as client:
            logo = await fetch_team_logo(team["name"], client)

        if logo:
            await db.teams.update_one(
                {"_id": ObjectId(team_id)},
                {"$set": {"logo_url": logo}}
            )
            return {"success": True, "logo_url": logo}
        return {"success": False, "message": "Logo non trovato su TheSportsDB"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/event-slugs")
async def sync_event_slugs(_=Depends(verify_admin_token)):
    """
    Genera/rigenera gli slug SEO ('inter-vs-parma') per tutti gli eventi.
    Garantisce unicità via suffisso numerico (-2, -3, ...) per match ripetuti.
    """
    try:
        from services.event_slug import backfill_all_slugs
        stats = await backfill_all_slugs()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.exception("Errore durante event-slugs sync")
        raise HTTPException(status_code=500, detail=str(e))
