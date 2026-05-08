"""
API Balance Checker — polling per provider che espongono il saldo + estimated da log.

Strategia:
1. Estimated balance: leggi log mese corrente, sottrai dal limite mensile config (db.api_budgets)
2. Real balance polling: per provider che lo permettono (DeepL, OpenAI, ecc.)

I risultati vengono salvati in db.api_balance_snapshots per trend.
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

import httpx

from database import db
from services.seo_keys import get_api_key

logger = logging.getLogger(__name__)


async def _get_estimated_balance(provider: str) -> Dict[str, Any]:
    """Stima saldo basato su log mese corrente vs budget mensile config."""
    today = datetime.now(timezone.utc)
    month_start = datetime(today.year, today.month, 1, tzinfo=timezone.utc)

    pipe = [
        {"$match": {"provider": provider, "ts": {"$gte": month_start}}},
        {"$group": {"_id": None, "total_cost": {"$sum": "$cost_usd"},
                    "count": {"$sum": 1}, "failures": {
                        "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}}}},
    ]
    res = await db.api_usage_logs.aggregate(pipe).to_list(1)
    used = float(res[0]["total_cost"]) if res else 0.0
    calls = int(res[0]["count"]) if res else 0
    fails = int(res[0]["failures"]) if res else 0

    budget_cfg = await db.api_budgets.find_one({"_id": provider}, {"_id": 0}) or {}
    monthly_limit = float(budget_cfg.get("monthly_limit_usd") or 0.0)
    remaining = (monthly_limit - used) if monthly_limit > 0 else None
    pct_used = (used / monthly_limit * 100) if monthly_limit > 0 else None

    return {
        "provider": provider,
        "method": "estimated_from_logs",
        "month_used_usd": round(used, 4),
        "monthly_limit_usd": monthly_limit,
        "remaining_usd": round(remaining, 4) if remaining is not None else None,
        "pct_used": round(pct_used, 2) if pct_used is not None else None,
        "calls_this_month": calls,
        "failures_this_month": fails,
    }


async def _check_deepl_balance() -> Optional[Dict[str, Any]]:
    """DeepL espone GET /v2/usage."""
    key = await get_api_key("deepl")
    if not key:
        return None
    base = "https://api-free.deepl.com" if ":fx" in str(key) else "https://api.deepl.com"
    try:
        async with httpx.AsyncClient(timeout=10) as cx:
            r = await cx.get(f"{base}/v2/usage", headers={"Authorization": f"DeepL-Auth-Key {key}"})
        if r.status_code != 200:
            return {"method": "real_polling", "error": f"HTTP {r.status_code}: {r.text[:200]}"}
        d = r.json()
        char_count = int(d.get("character_count") or 0)
        char_limit = int(d.get("character_limit") or 0)
        char_left = char_limit - char_count if char_limit > 0 else None
        return {
            "method": "real_polling",
            "char_used": char_count,
            "char_limit": char_limit,
            "char_left": char_left,
            "pct_used": round(char_count / char_limit * 100, 2) if char_limit > 0 else None,
        }
    except Exception as e:
        return {"method": "real_polling", "error": str(e)[:200]}


async def _check_openai_balance() -> Optional[Dict[str, Any]]:
    """OpenAI deprecato endpoint /v1/dashboard/billing/credit_grants ma alcuni utenti lo usano ancora."""
    key = await get_api_key("openai")
    if not key:
        return None
    return {"method": "estimated_from_logs", "note": "OpenAI billing API non più pubblica"}


async def get_provider_balance(provider: str) -> Dict[str, Any]:
    """Combina real polling (se disponibile) + estimated da log."""
    est = await _get_estimated_balance(provider)
    real = None

    if provider == "deepl":
        real = await _check_deepl_balance()
    elif provider == "openai":
        real = await _check_openai_balance()
    # Aggiungere altri provider qui se espongono balance API

    out = {**est}
    if real:
        out["real_polling"] = real

    out["ts"] = datetime.now(timezone.utc).isoformat()
    return out


PROVIDERS_TO_CHECK = ["claude", "gemini", "perplexity", "deepl", "dataforseo", "openai"]


async def snapshot_all_balances() -> Dict[str, Any]:
    """Snapshot di tutti i balance providers. Salvato in db.api_balance_snapshots."""
    out: Dict[str, Any] = {"providers": {}, "ts": datetime.now(timezone.utc).isoformat()}
    for p in PROVIDERS_TO_CHECK:
        try:
            out["providers"][p] = await get_provider_balance(p)
        except Exception as e:
            out["providers"][p] = {"error": str(e)[:200]}
    await db.api_balance_snapshots.insert_one({**out, "snap_at": datetime.now(timezone.utc)})
    return out
