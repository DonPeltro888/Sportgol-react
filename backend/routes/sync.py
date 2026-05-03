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


@router.post("/run-mix")
async def run_mix_sync(_=Depends(verify_admin_token)):
    """
    Esegue il MIX 5-fonti completo:
      1. OpenFootball (top leghe nazionali, JSON GitHub)
      2. matchesio.com (resto leghe)
      3. APIfootball.com (UEL/UECL/coppe se key configurata)
      4. TheSportsDB (coppe restanti, key '3' free)
      5. Backfill slugs

    Ritorna stats aggregate per fonte.
    """
    from datetime import datetime as dt, timezone as tz
    from database import db as _db

    overall = {
        "started_at": dt.now(tz.utc).isoformat(),
        "providers_run": [],
        "providers_skipped": [],
        "totals": {"inserted": 0, "updated": 0, "logos": 0},
    }

    async def _run_step(name: str, fn, *args, **kwargs):
        try:
            stats = await fn(*args, **kwargs)
            overall["providers_run"].append({
                "provider": name,
                "ok": stats.get("success", False),
                "inserted": stats.get("total_inserted", 0),
                "updated": stats.get("total_updated", 0),
                "logos_added": stats.get("logos_added", 0),
                "leagues_synced": stats.get("leagues_synced", 0),
                "leagues_empty": len(stats.get("leagues_empty", [])),
                "leagues_failed": len(stats.get("leagues_failed", [])),
                "error": stats.get("error"),
            })
            overall["totals"]["inserted"] += stats.get("total_inserted", 0)
            overall["totals"]["updated"] += stats.get("total_updated", 0)
            overall["totals"]["logos"] += stats.get("logos_added", 0)
        except Exception as e:
            overall["providers_run"].append({"provider": name, "ok": False, "error": str(e)[:200]})

    # STEP 1: OpenFootball (gratis, no key)
    from services.openfootball_sync import sync_via_openfootball
    await _run_step("openfootball", sync_via_openfootball)

    # STEP 2: matchesio (gratis, no key)
    from services.matchesio_sync import sync_all_competitions
    await _run_step("matchesio", sync_all_competitions, replace_all=False)

    # STEP 3: APIfootball.com (se key configurata e abilitata)
    settings_doc = await _db.settings.find_one({"_id": "integrations"}, {"_id": 0}) or {}
    af_cfg = settings_doc.get("apifootball", {})
    if af_cfg.get("enabled") and af_cfg.get("api_key"):
        from services.apifootball_sync import sync_via_apifootball
        await _run_step("apifootball", sync_via_apifootball)
    else:
        overall["providers_skipped"].append({"provider": "apifootball", "reason": "key non configurata o disabilitata"})

    # STEP 4: TheSportsDB (sempre runna, key '3' free di default)
    from services.thesportsdb_sync import sync_via_thesportsdb
    await _run_step("thesportsdb", sync_via_thesportsdb)

    overall["finished_at"] = dt.now(tz.utc).isoformat()
    overall["total_in_db"] = await _db.events.count_documents({})
    overall["success"] = True

    # Salva log MIX
    await _db.sync_logs.insert_one({
        **overall,
        "log_at": dt.now(tz.utc),
        "source": "mix",
        "total_inserted": overall["totals"]["inserted"],
        "total_updated": overall["totals"]["updated"],
        "logos_added": overall["totals"]["logos"],
    })
    return overall


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
