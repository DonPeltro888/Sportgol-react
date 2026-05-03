"""
Admin endpoints for managing 3rd-party integrations (API keys).
Storage: MongoDB collection 'settings' (singleton doc with _id='integrations').
Providers supported:
- api_football  (RapidAPI - https://rapidapi.com/api-sports/api/api-football)
- football_data (football-data.org)
"""
import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from database import db
from routes.admin_auth import verify_admin_token

router = APIRouter(prefix="/api/admin/integrations", tags=["admin-integrations"])

SETTINGS_ID = "integrations"

SUPPORTED_PROVIDERS = {"api_football", "football_data"}


class FootballApiConfig(BaseModel):
    provider: str  # 'api_football' | 'football_data'
    api_key: str
    enabled: bool = True


async def get_integrations_doc() -> dict:
    """Ritorna il documento settings (con default se mancante)."""
    doc = await db.settings.find_one({"_id": SETTINGS_ID}, {"_id": 0})
    if not doc:
        doc = {
            "football_api": {
                "provider": "api_football",
                "api_key": "",
                "enabled": False,
                "last_test": None,
                "last_test_result": None,
            }
        }
    return doc


def _mask(key: str) -> str:
    """Maschera la key mostrando solo gli ultimi 4 caratteri."""
    if not key:
        return ""
    if len(key) <= 8:
        return "***" + key[-2:]
    return key[:4] + "..." + key[-4:]


@router.get("")
async def get_integrations(_=Depends(verify_admin_token)):
    """Ritorna la configurazione corrente (API key mascherata)."""
    doc = await get_integrations_doc()
    fa = doc.get("football_api", {})
    return {
        "football_api": {
            "provider": fa.get("provider", "api_football"),
            "api_key_masked": _mask(fa.get("api_key", "")),
            "api_key_set": bool(fa.get("api_key")),
            "enabled": fa.get("enabled", False),
            "last_test": fa.get("last_test"),
            "last_test_result": fa.get("last_test_result"),
        }
    }


@router.put("/football-api")
async def update_football_api(config: FootballApiConfig, _=Depends(verify_admin_token)):
    """Salva/aggiorna la configurazione dell'API football."""
    if config.provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Provider non supportato. Scegli tra: {', '.join(SUPPORTED_PROVIDERS)}",
        )
    if not config.api_key or len(config.api_key) < 10:
        raise HTTPException(status_code=400, detail="API key troppo corta o mancante")

    await db.settings.update_one(
        {"_id": SETTINGS_ID},
        {
            "$set": {
                "football_api.provider": config.provider,
                "football_api.api_key": config.api_key,
                "football_api.enabled": config.enabled,
            }
        },
        upsert=True,
    )
    return {"success": True, "message": "Configurazione salvata"}


@router.post("/football-api/test")
async def test_football_api(_=Depends(verify_admin_token)):
    """Testa la connessione all'API football con la key attualmente salvata."""
    doc = await get_integrations_doc()
    fa = doc.get("football_api", {})
    api_key = fa.get("api_key", "")
    provider = fa.get("provider", "api_football")

    if not api_key:
        raise HTTPException(status_code=400, detail="Nessuna API key salvata. Inseriscila e salva prima di testare.")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            if provider == "api_football":
                # RapidAPI - endpoint di test: GET /status
                resp = await client.get(
                    "https://api-football-v1.p.rapidapi.com/v3/status",
                    headers={
                        "X-RapidAPI-Key": api_key,
                        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com",
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    account = data.get("response", {}).get("account", {})
                    requests_info = data.get("response", {}).get("requests", {})
                    result = {
                        "ok": True,
                        "provider": "API-Football (RapidAPI)",
                        "account_email": account.get("email"),
                        "requests_today": f"{requests_info.get('current', 0)} / {requests_info.get('limit_day', '?')}",
                        "plan": data.get("response", {}).get("subscription", {}).get("plan", "?"),
                    }
                elif resp.status_code in (401, 403):
                    result = {"ok": False, "error": "API key non valida o non autorizzata. Controlla di aver fatto Subscribe al piano Basic."}
                else:
                    result = {"ok": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

            elif provider == "football_data":
                # football-data.org - GET /v4/competitions/CL (Champions League) come test
                resp = await client.get(
                    "https://api.football-data.org/v4/competitions/CL",
                    headers={"X-Auth-Token": api_key},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    result = {
                        "ok": True,
                        "provider": "Football-Data.org",
                        "sample_competition": data.get("name"),
                        "note": "Key valida. Il piano free permette 10 req/min e copre 12 competizioni top.",
                    }
                elif resp.status_code == 403:
                    result = {"ok": False, "error": "Key valida ma accesso a questa competizione negato (possibile problema di piano)."}
                elif resp.status_code == 401:
                    result = {"ok": False, "error": "Key non valida."}
                else:
                    result = {"ok": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}
            else:
                result = {"ok": False, "error": "Provider sconosciuto"}

    except httpx.TimeoutException:
        result = {"ok": False, "error": "Timeout: l'API non ha risposto entro 15 secondi."}
    except Exception as e:
        result = {"ok": False, "error": f"Errore di rete: {str(e)}"}

    # Salva esito del test
    from datetime import datetime, timezone
    await db.settings.update_one(
        {"_id": SETTINGS_ID},
        {
            "$set": {
                "football_api.last_test": datetime.now(timezone.utc).isoformat(),
                "football_api.last_test_result": result,
            }
        },
        upsert=True,
    )
    return result


@router.delete("/football-api")
async def delete_football_api(_=Depends(verify_admin_token)):
    """Rimuove la key football API dal DB."""
    await db.settings.update_one(
        {"_id": SETTINGS_ID},
        {"$set": {"football_api.api_key": "", "football_api.enabled": False}},
        upsert=True,
    )
    return {"success": True, "message": "API key rimossa"}
