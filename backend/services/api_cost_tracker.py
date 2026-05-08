"""
API Cost Tracker — decorator che logga ogni chiamata API in db.api_usage_logs.

Usage (su una funzione async che fa una chiamata HTTP):
    from services.api_cost_tracker import track_api_usage

    @track_api_usage(provider="perplexity", op_type="sonar-pro")
    async def fetch_data(prompt, ...):
        # ... code ...
        return {
            "_tracking": {
                "tokens_in": 1234,
                "tokens_out": 567,
                "units_used": 1,         # OR direttamente cost via "cost_usd_override"
                "entity_type": "league",
                "entity_slug": "serie-a",
                "job_id": "...",
            },
            "data": {...}
        }

Il decorator misura:
- latency_ms
- success/failure + classified error_code
- cost_usd da pricing config
- ts UTC
"""
import asyncio
import logging
import re
import time
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, Optional

import httpx

from database import db
from services.api_pricing import compute_cost, get_pricing

logger = logging.getLogger(__name__)


def _classify_error(exc: Exception) -> Dict[str, str]:
    """Classifica eccezioni in error_code categorizzati."""
    msg = str(exc).lower()
    if isinstance(exc, httpx.TimeoutException) or "timeout" in msg:
        return {"error_code": "NETWORK_TIMEOUT", "error_msg": str(exc)[:300]}
    if isinstance(exc, httpx.ConnectError) or "connection" in msg:
        return {"error_code": "NETWORK_ERROR", "error_msg": str(exc)[:300]}
    if "rate limit" in msg or "429" in msg or "too many requests" in msg:
        return {"error_code": "RATE_LIMIT", "error_msg": str(exc)[:300]}
    if "401" in msg or "403" in msg or "auth" in msg or "api key" in msg or "unauthorized" in msg:
        return {"error_code": "AUTH_FAILED", "error_msg": str(exc)[:300]}
    if "402" in msg or "quota" in msg or "credit" in msg or "balance" in msg or "billing" in msg:
        return {"error_code": "QUOTA_EXCEEDED", "error_msg": str(exc)[:300]}
    if "invalid" in msg and ("json" in msg or "format" in msg or "response" in msg):
        return {"error_code": "INVALID_RESPONSE", "error_msg": str(exc)[:300]}
    if "5" in msg[:3]:  # 5xx
        return {"error_code": "INTERNAL_ERROR", "error_msg": str(exc)[:300]}
    return {"error_code": "UNKNOWN", "error_msg": str(exc)[:300]}


def _classify_http_status(status_code: int, body: str) -> Optional[Dict[str, str]]:
    """Classifica status code HTTP non-2xx."""
    if 200 <= status_code < 300:
        return None
    if status_code == 429:
        return {"error_code": "RATE_LIMIT", "error_msg": f"HTTP 429: {body[:200]}"}
    if status_code in (401, 403):
        return {"error_code": "AUTH_FAILED", "error_msg": f"HTTP {status_code}: {body[:200]}"}
    if status_code == 402:
        return {"error_code": "QUOTA_EXCEEDED", "error_msg": f"HTTP 402: {body[:200]}"}
    if status_code == 404:
        return {"error_code": "NOT_FOUND", "error_msg": f"HTTP 404: {body[:200]}"}
    if 500 <= status_code < 600:
        return {"error_code": "INTERNAL_ERROR", "error_msg": f"HTTP {status_code}: {body[:200]}"}
    return {"error_code": "INVALID_RESPONSE", "error_msg": f"HTTP {status_code}: {body[:200]}"}


def track_api_usage(provider: str, op_type: str, sub_type: Optional[str] = None):
    """Decorator: tracks ogni chiamata API.
    La funzione wrappata può ritornare un dict con `_tracking` per fornire
    cost details (tokens, units, entity context).
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start = time.time()
            ts = datetime.now(timezone.utc)
            log: Dict[str, Any] = {
                "provider": provider,
                "op_type": op_type,
                "sub_type": sub_type,
                "ts": ts,
                "status": "ok",
                "error_code": None,
                "error_msg": None,
                "latency_ms": 0,
                "cost_usd": 0.0,
                "units_used": 0,
                "tokens_in": 0,
                "tokens_out": 0,
                "entity_type": kwargs.get("_entity_type") or kwargs.get("entity_type"),
                "entity_slug": kwargs.get("_entity_slug") or kwargs.get("entity_slug"),
                "job_id": kwargs.get("_job_id") or kwargs.get("job_id"),
                "function": func.__name__,
            }

            try:
                result = await func(*args, **kwargs)
                # Estrai metadata di tracking dal risultato (se la funzione la fornisce)
                tracking = {}
                if isinstance(result, dict):
                    tracking = result.get("_tracking") or {}
                tokens_in = int(tracking.get("tokens_in") or 0)
                tokens_out = int(tracking.get("tokens_out") or 0)
                units = float(tracking.get("units_used") or 1)

                # Compute cost
                cost = 0.0
                if provider in ("claude", "gemini") and op_type != "vision" and "image" not in (sub_type or ""):
                    # LLM con tokens split
                    pricing_in = await get_pricing(provider, op_type, "input")
                    pricing_out = await get_pricing(provider, op_type, "output")
                    cost = compute_cost(pricing_in, tokens_in / 1000.0) + compute_cost(pricing_out, tokens_out / 1000.0)
                else:
                    pricing = await get_pricing(provider, op_type, sub_type)
                    if "cost_usd_override" in tracking:
                        cost = float(tracking["cost_usd_override"])
                    else:
                        cost = compute_cost(pricing, units)

                log.update({
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                    "units_used": units,
                    "cost_usd": round(cost, 6),
                    "entity_type": tracking.get("entity_type") or log.get("entity_type"),
                    "entity_slug": tracking.get("entity_slug") or log.get("entity_slug"),
                    "job_id": tracking.get("job_id") or log.get("job_id"),
                })
                return result
            except Exception as e:
                err = _classify_error(e)
                log["status"] = "failed"
                log.update(err)
                raise
            finally:
                log["latency_ms"] = int((time.time() - start) * 1000)
                try:
                    await db.api_usage_logs.insert_one(log)
                except Exception as db_err:
                    logger.error(f"api_cost_tracker: failed to write log: {db_err}")

        return wrapper
    return decorator


async def manual_log(
    provider: str, op_type: str,
    sub_type: Optional[str] = None,
    tokens_in: int = 0, tokens_out: int = 0,
    units_used: float = 1, cost_usd_override: Optional[float] = None,
    status: str = "ok",
    error_code: Optional[str] = None, error_msg: Optional[str] = None,
    latency_ms: int = 0,
    entity_type: Optional[str] = None, entity_slug: Optional[str] = None,
    job_id: Optional[str] = None,
    http_status: Optional[int] = None,
    response_body_preview: Optional[str] = None,
    function: Optional[str] = None,
):
    """API manuale per loggare una chiamata già eseguita (used by services with manual http calls)."""
    cost = 0.0
    if cost_usd_override is not None:
        cost = float(cost_usd_override)
    elif status == "ok":
        if provider in ("claude", "gemini") and op_type != "vision" and "image" not in (sub_type or ""):
            pricing_in = await get_pricing(provider, op_type, "input")
            pricing_out = await get_pricing(provider, op_type, "output")
            cost = compute_cost(pricing_in, tokens_in / 1000.0) + compute_cost(pricing_out, tokens_out / 1000.0)
        else:
            pricing = await get_pricing(provider, op_type, sub_type)
            cost = compute_cost(pricing, units_used)

    # Classify error from HTTP if needed
    if status == "failed" and not error_code and http_status:
        cls = _classify_http_status(http_status, response_body_preview or "")
        if cls:
            error_code = cls["error_code"]
            error_msg = cls["error_msg"]

    doc = {
        "provider": provider,
        "op_type": op_type,
        "sub_type": sub_type,
        "ts": datetime.now(timezone.utc),
        "status": status,
        "error_code": error_code,
        "error_msg": (error_msg[:500] if error_msg else None),
        "latency_ms": latency_ms,
        "cost_usd": round(cost, 6),
        "units_used": units_used,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "entity_type": entity_type,
        "entity_slug": entity_slug,
        "job_id": job_id,
        "function": function,
        "http_status": http_status,
    }
    try:
        await db.api_usage_logs.insert_one(doc)
    except Exception as db_err:
        logger.error(f"api_cost_tracker manual_log: {db_err}")
