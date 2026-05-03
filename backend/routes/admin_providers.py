"""
Admin endpoints per gestione integrazioni multiple (multi-provider).
Sostituisce il singleton 'football_api' con sistema esteso.
"""
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from database import db
from routes.admin_auth import verify_admin_token

router = APIRouter(prefix="/api/admin/providers", tags=["admin-providers"])

SETTINGS_ID = "integrations"

# Definizione di tutti i provider disponibili
PROVIDERS_CATALOG = {
    "openfootball": {
        "name": "OpenFootball",
        "category": "free",
        "needs_key": False,
        "free_tier": True,
        "description": "JSON pubblici su GitHub. Gratis e illimitato. Top leghe nazionali (Premier, Serie A, La Liga, Bundesliga, Ligue 1, ecc.).",
        "coverage": ["Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1", "Eredivisie", "Liga Portugal"],
        "signup_url": "https://github.com/openfootball/football.json",
        "docs_url": "https://github.com/openfootball/awesome-football",
    },
    "matchesio": {
        "name": "matchesio.com",
        "category": "free",
        "needs_key": False,
        "free_tier": True,
        "description": "Web scraping pubblico, gratis e illimitato. Buona copertura leghe nazionali ma nessuna copertura coppe europee.",
        "coverage": ["20+ leghe nazionali", "MLS", "Liga MX", "J1 League", "World Cup 2026"],
        "signup_url": "https://www.matchesio.com",
        "docs_url": "https://www.matchesio.com",
    },
    "thesportsdb": {
        "name": "TheSportsDB",
        "category": "freemium",
        "needs_key": True,
        "free_tier": True,
        "description": "Free key '3' (pubblica): 15 eventi futuri per lega. Premium $3/mese su Patreon: eventi illimitati. Copre TUTTE le competizioni.",
        "coverage": ["Europa League", "Conference League", "Coppa Italia", "FA Cup", "Champions League"],
        "signup_url": "https://www.patreon.com/thedatadb",
        "docs_url": "https://www.thesportsdb.com/documentation",
        "free_key_default": "3",
    },
    "football_data": {
        "name": "Football-Data.org",
        "category": "freemium",
        "needs_key": True,
        "free_tier": True,
        "description": "Free tier 10/min senza carta: top leghe + Champions League. Tier 1 €19/mese sblocca UEL, FA Cup, Coppa Italia.",
        "coverage": ["Champions League", "Premier League", "Serie A", "La Liga", "Bundesliga", "Ligue 1"],
        "signup_url": "https://www.football-data.org/client/register",
        "docs_url": "https://www.football-data.org/documentation/api",
    },
    "apifootball": {
        "name": "APIfootball.com",
        "category": "freemium",
        "needs_key": True,
        "free_tier": False,
        "description": "Trial 15 giorni gratis: copertura completa (UEL, UECL, coppe nazionali, World Cup, AFC, CAF). Dopo trial: $21/mese (European plan).",
        "coverage": ["Tutte le competizioni mondiali", "UEL", "UECL", "Coppa Italia", "FA Cup", "Copa del Rey", "World Cup 2026"],
        "signup_url": "https://apifootball.com/register/",
        "docs_url": "https://apifootball.com/documentation",
    },
    "api_football": {
        "name": "API-Football (api-sports.io)",
        "category": "freemium",
        "needs_key": True,
        "free_tier": True,
        "description": "Free tier 100 req/giorno. ⚠️ Limitazione: il piano free fornisce solo dati STORICI (stagioni 2021-2024), non la stagione corrente. Pro $25/mese sblocca tutto.",
        "coverage": ["Storico 2021-2024 free", "Stagione corrente solo paid"],
        "signup_url": "https://dashboard.api-football.com/register",
        "docs_url": "https://www.api-football.com/documentation-v3",
    },
}


class ProviderConfig(BaseModel):
    api_key: str
    enabled: bool = True


def _mask(key: str) -> str:
    if not key or len(key) < 4:
        return ""
    if len(key) <= 8:
        return "***" + key[-2:]
    return key[:4] + "..." + key[-4:]


@router.get("")
async def list_providers(_=Depends(verify_admin_token)):
    """Ritorna lista provider con stato attuale (key configurate, ultimo test)."""
    doc = await db.settings.find_one({"_id": SETTINGS_ID}, {"_id": 0}) or {}
    
    result = []
    for slug, cat in PROVIDERS_CATALOG.items():
        # Mappa slug → nome campo nel doc
        field = "football_api" if slug == "api_football" else slug
        cfg = doc.get(field, {})
        result.append({
            "slug": slug,
            **cat,
            "configured": bool(cfg.get("api_key")) if cat["needs_key"] else True,
            "enabled": cfg.get("enabled", True if not cat["needs_key"] else False),
            "api_key_masked": _mask(cfg.get("api_key", "")),
            "last_test_at": cfg.get("last_test"),
            "last_test_result": cfg.get("last_test_result"),
        })
    return {"providers": result}


@router.put("/{provider_slug}")
async def update_provider(provider_slug: str, config: ProviderConfig, _=Depends(verify_admin_token)):
    """Salva la configurazione di un provider specifico."""
    if provider_slug not in PROVIDERS_CATALOG:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_slug}' sconosciuto")
    cat = PROVIDERS_CATALOG[provider_slug]
    if cat["needs_key"] and (not config.api_key or len(config.api_key) < 5):
        raise HTTPException(status_code=400, detail="API key mancante o troppo corta")
    
    field = "football_api" if provider_slug == "api_football" else provider_slug
    await db.settings.update_one(
        {"_id": SETTINGS_ID},
        {"$set": {
            f"{field}.provider": provider_slug if provider_slug == "api_football" else field,
            f"{field}.api_key": config.api_key,
            f"{field}.enabled": config.enabled,
        }},
        upsert=True,
    )
    return {"success": True, "message": f"Configurazione '{cat['name']}' salvata"}


@router.delete("/{provider_slug}")
async def delete_provider(provider_slug: str, _=Depends(verify_admin_token)):
    if provider_slug not in PROVIDERS_CATALOG:
        raise HTTPException(status_code=404)
    field = "football_api" if provider_slug == "api_football" else provider_slug
    await db.settings.update_one(
        {"_id": SETTINGS_ID},
        {"$set": {f"{field}.api_key": "", f"{field}.enabled": False}},
        upsert=True,
    )
    return {"success": True}


@router.post("/{provider_slug}/test")
async def test_provider(provider_slug: str, _=Depends(verify_admin_token)):
    """Testa la connessione a un provider."""
    if provider_slug not in PROVIDERS_CATALOG:
        raise HTTPException(status_code=404)
    
    result = {"ok": False, "error": "Not implemented"}
    
    try:
        if provider_slug == "openfootball":
            # No key, test fetch JSON
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get("https://raw.githubusercontent.com/openfootball/football.json/master/2025-26/en.1.json")
                if r.status_code == 200:
                    data = r.json()
                    result = {"ok": True, "provider": "OpenFootball", "matches_premier": len(data.get("matches", []))}
                else:
                    result = {"ok": False, "error": f"HTTP {r.status_code}"}
        
        elif provider_slug == "matchesio":
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get("https://www.matchesio.com/it/competition/serie-a/export/json/", follow_redirects=True)
                if r.status_code == 200:
                    try:
                        data = r.json()
                        result = {"ok": True, "provider": "matchesio.com", "matches_serie_a": len(data) if isinstance(data, list) else 0}
                    except Exception:
                        result = {"ok": False, "error": "Risposta non JSON"}
                else:
                    result = {"ok": False, "error": f"HTTP {r.status_code}"}
        
        elif provider_slug == "thesportsdb":
            from services.thesportsdb_sync import _get_sportsdb_key
            key = await _get_sportsdb_key()
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"https://www.thesportsdb.com/api/v1/json/{key}/eventsseason.php?id=4481&s=2025-2026")
                if r.status_code == 200:
                    data = r.json()
                    events = data.get("events") or []
                    result = {"ok": True, "provider": "TheSportsDB", "europa_league_events": len(events), "key_type": "free pubblica" if key == "3" else "premium"}
                else:
                    result = {"ok": False, "error": f"HTTP {r.status_code}"}
        
        elif provider_slug == "football_data":
            doc = await db.settings.find_one({"_id": SETTINGS_ID}, {"_id": 0}) or {}
            key = doc.get("football_data", {}).get("api_key")
            if not key:
                # backward compat: l'utente potrebbe aver salvato in football_api con provider=football_data
                fa = doc.get("football_api", {})
                if fa.get("provider") == "football_data":
                    key = fa.get("api_key")
            if not key:
                result = {"ok": False, "error": "Nessuna API key configurata"}
            else:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    r = await client.get("https://api.football-data.org/v4/competitions/CL", headers={"X-Auth-Token": key})
                    if r.status_code == 200:
                        result = {"ok": True, "provider": "Football-Data.org", "champions_league_access": True}
                    elif r.status_code == 403:
                        result = {"ok": False, "error": "Key valida ma piano free non copre questa competizione"}
                    else:
                        result = {"ok": False, "error": f"HTTP {r.status_code}"}
        
        elif provider_slug == "apifootball":
            from services.apifootball_sync import test_apifootball_connection
            result = await test_apifootball_connection()
        
        elif provider_slug == "api_football":
            doc = await db.settings.find_one({"_id": SETTINGS_ID}, {"_id": 0}) or {}
            key = doc.get("football_api", {}).get("api_key")
            if not key:
                result = {"ok": False, "error": "Nessuna API key"}
            else:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    r = await client.get("https://v3.football.api-sports.io/status", headers={"x-apisports-key": key})
                    if r.status_code == 200:
                        d = r.json()
                        if d.get("errors"):
                            result = {"ok": False, "error": str(d["errors"])}
                        else:
                            resp = d.get("response", {})
                            sub = resp.get("subscription", {})
                            req = resp.get("requests", {})
                            result = {
                                "ok": True,
                                "provider": "API-Football (api-sports.io)",
                                "plan": sub.get("plan"),
                                "requests": f"{req.get('current')}/{req.get('limit_day')}",
                                "warning": "Free tier copre solo stagioni 2021-2024 (storiche). Per stagione corrente serve piano Pro $25/mese." if sub.get("plan") == "Free" else None,
                            }
                    else:
                        result = {"ok": False, "error": f"HTTP {r.status_code}"}
    except Exception as e:
        result = {"ok": False, "error": str(e)}
    
    # Salva esito
    field = "football_api" if provider_slug == "api_football" else provider_slug
    await db.settings.update_one(
        {"_id": SETTINGS_ID},
        {"$set": {
            f"{field}.last_test": datetime.now(timezone.utc).isoformat(),
            f"{field}.last_test_result": result,
        }},
        upsert=True,
    )
    return result


@router.get("/coverage-report")
async def coverage_report(_=Depends(verify_admin_token)):
    """
    Ritorna per ogni lega/competizione:
      - quanti eventi futuri
      - da quale fonte (source) provengono
      - se è "morta" (0 eventi e ultimo evento > 6 mesi fa)
    """
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    six_months_ago = (datetime.now(timezone.utc).replace(microsecond=0) - 
                      __import__("datetime").timedelta(days=180)).strftime("%Y-%m-%d")
    
    leagues = await db.leagues.find({}, {"_id": 0, "name": 1, "slug": 1, "type": 1, "country": 1, "active": 1}).to_list(200)
    
    report = []
    for lg in leagues:
        name = lg.get("name", "")
        # Eventi futuri per questa lega (case insensitive)
        future_count = await db.events.count_documents({
            "league": {"$regex": f"^{name}$", "$options": "i"},
            "sort_date": {"$gte": today_str},
        })
        # Distribuzione per source
        sources_pipeline = [
            {"$match": {
                "league": {"$regex": f"^{name}$", "$options": "i"},
                "sort_date": {"$gte": today_str},
            }},
            {"$group": {"_id": "$source", "count": {"$sum": 1}}},
        ]
        sources = []
        async for s in db.events.aggregate(sources_pipeline):
            sources.append({"source": s.get("_id") or "matchesio", "count": s["count"]})
        
        # Ultimo evento (anche passato)
        last = await db.events.find_one(
            {"league": {"$regex": f"^{name}$", "$options": "i"}},
            {"_id": 0, "sort_date": 1, "date": 1},
            sort=[("sort_date", -1)],
        )
        last_event_date = (last or {}).get("sort_date", "")
        # Status:
        # - active: ha eventi futuri
        # - dormant: 0 futuri ma ultimo evento è recente (< 6 mesi)
        # - dead: 0 futuri E ultimo evento > 6 mesi fa o nessun evento
        if future_count > 0:
            status = "active"
        elif last_event_date and last_event_date[:10] > six_months_ago:
            status = "dormant"
        else:
            status = "dead"
        
        report.append({
            "name": name,
            "slug": lg.get("slug"),
            "type": lg.get("type"),
            "country": lg.get("country"),
            "active_in_db": lg.get("active", True),
            "future_events": future_count,
            "sources": sources,
            "last_event_date": last_event_date[:10] if last_event_date else None,
            "status": status,
        })
    
    # Ordina: dead per ultime, dormant in mezzo, active in cima
    order = {"active": 0, "dormant": 1, "dead": 2}
    report.sort(key=lambda x: (order[x["status"]], -x["future_events"]))
    
    return {
        "total_leagues": len(report),
        "active": sum(1 for r in report if r["status"] == "active"),
        "dormant": sum(1 for r in report if r["status"] == "dormant"),
        "dead": sum(1 for r in report if r["status"] == "dead"),
        "leagues": report,
    }
