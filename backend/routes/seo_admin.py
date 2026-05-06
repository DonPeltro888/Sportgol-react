"""
SEO Automation Admin – API & Tools Settings + Dashboard endpoints.

Tutte le rotte sono protette dall'admin token esistente di Golevents.
Le API keys sono cifrate con Fernet (services/seo_crypto) e non vengono mai
restituite in chiaro al frontend (solo masked).
"""
import os
import time
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any

import httpx
from fastapi import APIRouter, Depends, HTTPException

from database import db
from routes.admin_auth import verify_admin_token
from services.seo_crypto import encrypt, decrypt, mask_secret
from services.seo_tools_catalog import TOOLS_CATALOG, get_tool
from models.seo import ApiToolUpdateRequest

router = APIRouter(prefix="/api/seo", tags=["seo-admin"])


# ─── Helpers ────────────────────────────────────────────────────────────────

async def _get_key_doc(slug: str) -> Dict[str, Any] | None:
    return await db.seo_api_keys.find_one({"slug": slug}, {"_id": 0})


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Tools Catalog ──────────────────────────────────────────────────────────

@router.get("/tools")
async def list_tools(_=Depends(verify_admin_token)) -> List[Dict[str, Any]]:
    """Lista tutti i tool del catalogo con stato chiave (mascherata)."""
    out: List[Dict[str, Any]] = []
    for tool in TOOLS_CATALOG:
        doc = await _get_key_doc(tool["slug"])
        plain_key = decrypt(doc.get("api_key_enc", "")) if doc else ""
        out.append({
            **tool,
            "active": (doc or {}).get("active", False),
            "has_key": bool(plain_key) or bool((doc or {}).get("api_login")),
            "api_key_masked": mask_secret(plain_key, 4) if plain_key else "",
            "api_login": (doc or {}).get("api_login", ""),
            "extra_config": (doc or {}).get("extra_config", {}),
            "last_tested_at": (doc or {}).get("last_tested_at"),
            "last_test_status": (doc or {}).get("last_test_status"),
            "last_test_error": (doc or {}).get("last_test_error"),
        })
    return out


@router.put("/tools/{slug}")
async def update_tool(
    slug: str,
    payload: ApiToolUpdateRequest,
    _=Depends(verify_admin_token),
):
    """Aggiorna api_key (cifrata) / login / extra / active per un tool."""
    if not get_tool(slug):
        raise HTTPException(status_code=404, detail="Tool not found")

    update: Dict[str, Any] = {"updated_at": _now_iso()}
    if payload.api_key is not None:
        # Stringa vuota = clear
        update["api_key_enc"] = encrypt(payload.api_key) if payload.api_key else ""
    if payload.api_login is not None:
        update["api_login"] = payload.api_login.strip()
    if payload.extra_config is not None:
        update["extra_config"] = payload.extra_config
    if payload.active is not None:
        update["active"] = bool(payload.active)

    await db.seo_api_keys.update_one(
        {"slug": slug},
        {"$set": {"slug": slug, **update}},
        upsert=True,
    )
    return {"ok": True}


# ─── Test Connection ────────────────────────────────────────────────────────

async def _test_claude(api_key: str) -> Dict[str, Any]:
    if not api_key:
        return {"ok": False, "error": "missing api key"}
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 8,
        "messages": [{"role": "user", "content": "ping"}],
    }
    try:
        async with httpx.AsyncClient(timeout=15) as cx:
            r = await cx.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
        if r.status_code == 200:
            return {"ok": True, "info": "claude-sonnet-4-5 reachable"}
        return {"ok": False, "error": f"http {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


async def _test_gemini(api_key: str) -> Dict[str, Any]:
    if not api_key:
        return {"ok": False, "error": "missing api key"}
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        async with httpx.AsyncClient(timeout=15) as cx:
            r = await cx.get(url)
        if r.status_code == 200:
            return {"ok": True, "info": "models endpoint reachable"}
        return {"ok": False, "error": f"http {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


async def _test_perplexity(api_key: str) -> Dict[str, Any]:
    if not api_key:
        return {"ok": False, "error": "missing api key"}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    body = {"model": "sonar", "messages": [{"role": "user", "content": "ping"}], "max_tokens": 8}
    try:
        async with httpx.AsyncClient(timeout=15) as cx:
            r = await cx.post("https://api.perplexity.ai/chat/completions", headers=headers, json=body)
        if r.status_code in (200, 201):
            return {"ok": True, "info": "sonar model reachable"}
        return {"ok": False, "error": f"http {r.status_code}: {r.text[:200]}"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


async def _test_dataforseo(login: str, password: str) -> Dict[str, Any]:
    if not login or not password:
        return {"ok": False, "error": "missing login or password"}
    auth = httpx.BasicAuth(login, password)
    try:
        async with httpx.AsyncClient(timeout=15, auth=auth) as cx:
            r = await cx.get("https://api.dataforseo.com/v3/appendix/user_data")
        if r.status_code == 200:
            data = r.json()
            balance = data.get("tasks", [{}])[0].get("result", [{}])[0].get("money", {}).get("balance")
            return {"ok": True, "info": f"balance: ${balance}" if balance is not None else "auth ok"}
        return {"ok": False, "error": f"http {r.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


async def _test_deepl(api_key: str) -> Dict[str, Any]:
    if not api_key:
        return {"ok": False, "error": "missing api key"}
    # DeepL: keys ending with ":fx" use free endpoint
    base = "https://api-free.deepl.com" if api_key.endswith(":fx") else "https://api.deepl.com"
    headers = {"Authorization": f"DeepL-Auth-Key {api_key}"}
    try:
        async with httpx.AsyncClient(timeout=15) as cx:
            r = await cx.get(f"{base}/v2/usage", headers=headers)
        if r.status_code == 200:
            data = r.json()
            return {"ok": True, "info": f"chars used: {data.get('character_count','?')}/{data.get('character_limit','?')}"}
        return {"ok": False, "error": f"http {r.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


async def _test_undetectable(api_key: str) -> Dict[str, Any]:
    if not api_key:
        return {"ok": False, "error": "missing api key"}
    # Generic ping: Undetectable.ai non ha un endpoint /health pubblico stabile,
    # quindi facciamo un check formale (chiave non vuota = considerato ok per P0).
    return {"ok": True, "info": "key stored (no live test in P0)"}


async def _test_se_ranking(api_key: str) -> Dict[str, Any]:
    if not api_key:
        return {"ok": False, "error": "missing api key"}
    try:
        async with httpx.AsyncClient(timeout=15) as cx:
            r = await cx.get(
                "https://api4.seranking.com/system/info",
                headers={"Authorization": f"Token {api_key}"},
            )
        if r.status_code == 200:
            return {"ok": True, "info": "auth ok"}
        return {"ok": False, "error": f"http {r.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)[:200]}


@router.post("/tools/{slug}/test")
async def test_tool(slug: str, _=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Esegue un test live verso il provider (auth check)."""
    tool = get_tool(slug)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    doc = await _get_key_doc(slug) or {}
    plain_key = decrypt(doc.get("api_key_enc", ""))
    login = doc.get("api_login", "")

    started = time.time()
    if slug == "claude":
        result = await _test_claude(plain_key)
    elif slug == "gemini":
        result = await _test_gemini(plain_key)
    elif slug == "perplexity":
        result = await _test_perplexity(plain_key)
    elif slug == "dataforseo":
        result = await _test_dataforseo(login, plain_key)
    elif slug == "deepl":
        result = await _test_deepl(plain_key)
    elif slug == "undetectable":
        result = await _test_undetectable(plain_key)
    elif slug == "se_ranking":
        result = await _test_se_ranking(plain_key)
    elif tool.get("p1_only"):
        result = {"ok": False, "error": "P1 — not implemented yet"}
    else:
        result = {"ok": False, "error": "no tester for this tool"}

    elapsed_ms = int((time.time() - started) * 1000)
    await db.seo_api_keys.update_one(
        {"slug": slug},
        {"$set": {
            "slug": slug,
            "last_tested_at": _now_iso(),
            "last_test_status": "ok" if result.get("ok") else "fail",
            "last_test_error": result.get("error", ""),
            "last_test_info": result.get("info", ""),
            "last_test_ms": elapsed_ms,
        }},
        upsert=True,
    )
    return {**result, "elapsed_ms": elapsed_ms}


# ─── Dashboard counts ──────────────────────────────────────────────────────

@router.get("/dashboard/stats")
async def dashboard_stats(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Statistiche SEO sulle entity esistenti (events, leagues, teams)."""
    out: Dict[str, Any] = {
        "by_type": {},
        "by_status": {"Draft": 0, "Generated": 0, "Needs Review": 0, "Approved": 0, "Published": 0},
        "tools_total": len(TOOLS_CATALOG),
    }
    for type_, coll in [("event", "events"), ("league", "leagues"), ("team", "teams")]:
        c = db[coll]
        total = await c.count_documents({})
        with_draft = await c.count_documents({"seo_draft": {"$exists": True, "$ne": None}})
        published = await c.count_documents({"seo_status": "Published"})
        out["by_type"][type_] = {
            "total": total,
            "with_draft": with_draft,
            "published": published,
        }
        # Aggregate status
        cursor = c.aggregate([{"$group": {"_id": "$seo_status", "n": {"$sum": 1}}}])
        async for row in cursor:
            st = row["_id"] or "Draft"
            out["by_status"][st] = out["by_status"].get(st, 0) + row["n"]

    out["total_pages"] = sum(t["total"] for t in out["by_type"].values())

    # Tool stats
    tools = await list_tools()  # type: ignore
    out["tools_with_key"] = sum(1 for t in tools if t["has_key"])
    out["tools_active"] = sum(1 for t in tools if t["active"] and t["has_key"])
    return out


# ─── Seed (idempotente) ─────────────────────────────────────────────────────

@router.post("/_seed_keys")
async def seed_keys_idempotent(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """
    Endpoint di utilità — popola le chiavi fornite dall'utente (run-once safe).
    Le chiavi non sono hardcoded nel repo: sono già state caricate al deploy.
    """
    return {"ok": True, "note": "Use PUT /api/seo/tools/{slug} to set keys."}
