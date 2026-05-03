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


@router.post("/football-api")
async def sync_football_api(_=Depends(verify_admin_token)):
    """
    Sync eventi e loghi tramite il provider configurato (api_football OR football_data).
    Richiede API key configurata in /admin/integrations.
    """
    try:
        # Determina provider
        doc = await db.settings.find_one({"_id": "integrations"}, {"_id": 0})
        if not doc:
            raise HTTPException(status_code=400, detail="Nessuna integrazione configurata. Vai in Admin → Integrazioni API.")
        provider = doc.get("football_api", {}).get("provider", "api_football")

        if provider == "api_football":
            from services.football_api_sync import sync_via_api_football
            stats = await sync_via_api_football()
        elif provider == "football_data":
            from services.football_data_sync import sync_via_football_data
            stats = await sync_via_football_data()
        else:
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' sconosciuto.")

        if not stats.get("success"):
            raise HTTPException(status_code=400, detail=stats.get("error", "Sync fallito"))
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Errore durante sync Football API")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fill-missing")
async def sync_fill_missing(_=Depends(verify_admin_token)):
    """
    MIX intelligente: identifica le leghe vuote nel DB e le riempie via API esterna.
    Risparmia chiamate API perché tocca solo le leghe veramente mancanti.
    """
    try:
        # Trova le leghe vuote (0 eventi futuri)
        from datetime import datetime, timezone as tz
        today = datetime.now(tz.utc).strftime("%Y-%m-%d")
        all_leagues = await db.leagues.find({"active": {"$ne": False}}, {"_id": 0, "name": 1}).to_list(100)
        empty_leagues = []
        for lg in all_leagues:
            name = lg.get("name", "")
            # Match case-insensitive: gli eventi hanno league uppercase ("SERIE A") mentre leagues "Serie A"
            count = await db.events.count_documents({
                "league": {"$regex": f"^{name}$", "$options": "i"},
                "sort_date": {"$gte": today}
            })
            if count == 0:
                empty_leagues.append(name)

        if not empty_leagues:
            return {"success": True, "message": "Nessuna lega vuota trovata. Tutte le competizioni hanno eventi.", "filled_leagues": []}

        # Determina provider
        doc = await db.settings.find_one({"_id": "integrations"}, {"_id": 0})
        if not doc:
            raise HTTPException(status_code=400, detail="API esterna non configurata. Vai in Admin → Integrazioni API.")
        provider = doc.get("football_api", {}).get("provider", "api_football")

        if provider == "football_data":
            from services.football_data_sync import sync_via_football_data
            stats = await sync_via_football_data(only_empty_leagues=empty_leagues)
        elif provider == "api_football":
            # API-Football non supporta filtro per nome lega in questo flusso; fa sync completa
            from services.football_api_sync import sync_via_api_football
            stats = await sync_via_api_football()
        else:
            raise HTTPException(status_code=400, detail=f"Provider '{provider}' sconosciuto.")

        if not stats.get("success"):
            raise HTTPException(status_code=400, detail=stats.get("error", "Sync fallito"))
        stats["empty_leagues_targeted"] = empty_leagues
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Errore durante fill-missing")
        raise HTTPException(status_code=500, detail=str(e))
