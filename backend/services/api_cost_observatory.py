"""
Cost Observatory aggregations + backfill from seo_jobs.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from database import db
from services.api_pricing import DEFAULT_PRICING, compute_cost, get_pricing

logger = logging.getLogger(__name__)


async def overview_stats() -> Dict[str, Any]:
    """Stat principali per la dashboard top section."""
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    week_start = today_start - timedelta(days=7)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    async def _stats(since: datetime):
        pipe = [
            {"$match": {"ts": {"$gte": since}}},
            {"$group": {
                "_id": None,
                "calls": {"$sum": 1},
                "cost": {"$sum": "$cost_usd"},
                "fails": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
                "avg_lat": {"$avg": "$latency_ms"},
            }},
        ]
        r = await db.api_usage_logs.aggregate(pipe).to_list(1)
        if r:
            return {"calls": r[0]["calls"], "cost": float(r[0]["cost"] or 0),
                    "fails": r[0]["fails"], "success_rate": (r[0]["calls"] - r[0]["fails"]) / max(r[0]["calls"], 1) * 100,
                    "avg_latency_ms": int(r[0]["avg_lat"] or 0)}
        return {"calls": 0, "cost": 0.0, "fails": 0, "success_rate": 100.0, "avg_latency_ms": 0}

    today = await _stats(today_start)
    week = await _stats(week_start)
    month = await _stats(month_start)

    # Forecast: linearizzazione spesa mese
    days_passed = max(1, (now - month_start).days + 1)
    days_in_month = 30
    daily_avg = month["cost"] / days_passed if days_passed else 0
    forecast = round(daily_avg * days_in_month, 2)

    # Top provider questo mese
    top_pipe = [
        {"$match": {"ts": {"$gte": month_start}}},
        {"$group": {"_id": "$provider", "cost": {"$sum": "$cost_usd"}, "calls": {"$sum": 1}}},
        {"$sort": {"cost": -1}}, {"$limit": 1},
    ]
    top_r = await db.api_usage_logs.aggregate(top_pipe).to_list(1)
    top_provider = top_r[0]["_id"] if top_r else "—"

    return {
        "today": today, "week": week, "month": month,
        "forecast_month_usd": forecast,
        "top_provider": top_provider,
        "ts": now.isoformat(),
    }


async def daily_chart(days: int = 30) -> List[Dict[str, Any]]:
    """Time-series spesa giornaliera ultimi N giorni."""
    now = datetime.now(timezone.utc)
    since = datetime(now.year, now.month, now.day, tzinfo=timezone.utc) - timedelta(days=days - 1)
    pipe = [
        {"$match": {"ts": {"$gte": since}}},
        {"$group": {
            "_id": {"day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$ts"}},
                    "provider": "$provider"},
            "cost": {"$sum": "$cost_usd"},
            "calls": {"$sum": 1},
        }},
        {"$sort": {"_id.day": 1}},
    ]
    rows = await db.api_usage_logs.aggregate(pipe).to_list(None)
    by_day: Dict[str, Dict[str, Any]] = {}
    providers = set()
    for r in rows:
        day = r["_id"]["day"]
        prov = r["_id"]["provider"]
        providers.add(prov)
        if day not in by_day:
            by_day[day] = {"day": day, "total": 0.0}
        by_day[day][prov] = round(float(r["cost"]), 4)
        by_day[day]["total"] += float(r["cost"])

    out = sorted(by_day.values(), key=lambda x: x["day"])
    return out


async def by_provider() -> List[Dict[str, Any]]:
    """Aggregato per provider con last-used, calls, cost month, fail rate, avg latency."""
    now = datetime.now(timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    pipe = [
        {"$facet": {
            "month_stats": [
                {"$match": {"ts": {"$gte": month_start}}},
                {"$group": {"_id": "$provider", "cost": {"$sum": "$cost_usd"},
                            "calls": {"$sum": 1},
                            "fails": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
                            "avg_lat": {"$avg": "$latency_ms"},
                            "tokens_in": {"$sum": "$tokens_in"},
                            "tokens_out": {"$sum": "$tokens_out"}}},
            ],
            "last_used": [
                {"$sort": {"ts": -1}},
                {"$group": {"_id": "$provider", "last_used": {"$first": "$ts"},
                            "last_status": {"$first": "$status"}}},
            ],
        }},
    ]
    res = await db.api_usage_logs.aggregate(pipe).to_list(1)
    if not res:
        return []

    month_map = {r["_id"]: r for r in res[0]["month_stats"]}
    last_map = {r["_id"]: r for r in res[0]["last_used"]}

    # Budget map
    budgets = {}
    async for b in db.api_budgets.find({}, {"_id": 1, "monthly_limit_usd": 1, "warning_pct": 1}):
        budgets[b["_id"]] = b

    out = []
    all_providers = set(month_map.keys()) | set(last_map.keys())
    for p in all_providers:
        m = month_map.get(p, {})
        lu = last_map.get(p, {})
        b = budgets.get(p, {})
        cost = float(m.get("cost") or 0)
        limit = float(b.get("monthly_limit_usd") or 0)
        pct = (cost / limit * 100) if limit > 0 else None
        out.append({
            "provider": p,
            "cost_month_usd": round(cost, 4),
            "calls_month": int(m.get("calls") or 0),
            "fails_month": int(m.get("fails") or 0),
            "tokens_in_month": int(m.get("tokens_in") or 0),
            "tokens_out_month": int(m.get("tokens_out") or 0),
            "success_rate_pct": round((1 - (m.get("fails") or 0) / max(m.get("calls") or 1, 1)) * 100, 1),
            "avg_latency_ms": int(m.get("avg_lat") or 0),
            "last_used_at": lu.get("last_used").isoformat() if lu.get("last_used") else None,
            "last_status": lu.get("last_status"),
            "monthly_limit_usd": limit if limit > 0 else None,
            "budget_pct": round(pct, 2) if pct is not None else None,
            "budget_status": "exceeded" if pct and pct >= 100 else
                              "warning" if pct and pct >= float(b.get("warning_pct") or 80) else "ok",
        })
    out.sort(key=lambda x: x["cost_month_usd"], reverse=True)
    return out


async def top_expensive_entities(days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
    """Top entità più costose (cost totale aggregato)."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    pipe = [
        {"$match": {"ts": {"$gte": since}, "entity_slug": {"$ne": None}}},
        {"$group": {
            "_id": {"type": "$entity_type", "slug": "$entity_slug"},
            "cost": {"$sum": "$cost_usd"},
            "calls": {"$sum": 1},
            "providers": {"$addToSet": "$provider"},
        }},
        {"$sort": {"cost": -1}}, {"$limit": limit},
    ]
    rows = await db.api_usage_logs.aggregate(pipe).to_list(limit)
    return [{
        "entity_type": r["_id"]["type"], "entity_slug": r["_id"]["slug"],
        "cost_usd": round(float(r["cost"]), 4), "calls": r["calls"],
        "providers": r["providers"],
    } for r in rows]


async def by_entity_type(days: int = 30) -> List[Dict[str, Any]]:
    """Cost per generation type (event vs team vs league)."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    pipe = [
        {"$match": {"ts": {"$gte": since}, "entity_type": {"$ne": None}}},
        {"$group": {"_id": "$entity_type",
                    "cost": {"$sum": "$cost_usd"}, "calls": {"$sum": 1},
                    "entities": {"$addToSet": "$entity_slug"}}},
    ]
    rows = await db.api_usage_logs.aggregate(pipe).to_list(None)
    return [{
        "entity_type": r["_id"], "cost_usd": round(float(r["cost"]), 4),
        "calls": r["calls"], "unique_entities": len(r["entities"]),
        "avg_cost_per_entity": round(float(r["cost"]) / max(len(r["entities"]), 1), 4),
    } for r in rows]


async def list_logs(limit: int = 100, offset: int = 0,
                    provider: Optional[str] = None, status: Optional[str] = None,
                    entity_slug: Optional[str] = None,
                    error_code: Optional[str] = None) -> Dict[str, Any]:
    flt: Dict[str, Any] = {}
    if provider:
        flt["provider"] = provider
    if status:
        flt["status"] = status
    if entity_slug:
        flt["entity_slug"] = entity_slug
    if error_code:
        flt["error_code"] = error_code
    cursor = db.api_usage_logs.find(flt, {"_id": 0}).sort("ts", -1).skip(offset).limit(limit)
    items = []
    async for d in cursor:
        if isinstance(d.get("ts"), datetime):
            d["ts"] = d["ts"].isoformat()
        items.append(d)
    total = await db.api_usage_logs.count_documents(flt)
    return {"items": items, "total": total, "limit": limit, "offset": offset}


async def latency_distribution(provider: Optional[str] = None, days: int = 7) -> Dict[str, Any]:
    """p50/p95 latency per provider."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    flt: Dict[str, Any] = {"ts": {"$gte": since}, "status": "ok"}
    if provider:
        flt["provider"] = provider
    pipe = [
        {"$match": flt},
        {"$group": {"_id": "$provider", "lats": {"$push": "$latency_ms"}, "count": {"$sum": 1}}},
    ]
    rows = await db.api_usage_logs.aggregate(pipe).to_list(None)
    out = []
    for r in rows:
        lats = sorted(r["lats"] or [])
        n = len(lats)
        p50 = lats[n // 2] if n else 0
        p95 = lats[int(n * 0.95)] if n else 0
        out.append({"provider": r["_id"], "count": n,
                    "p50_ms": int(p50), "p95_ms": int(p95)})
    return {"rows": out}


async def backfill_from_seo_jobs(days: int = 30) -> Dict[str, Any]:
    """Ricostruisce log retroattivi dai seo_jobs già completati.
    Stima cost based on default pricing for each step.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)
    cursor = db.seo_jobs.find(
        {"created_at": {"$gte": since}, "status": "succeeded"},
        {"_id": 1, "target_type": 1, "target_id": 1, "created_at": 1, "completed_at": 1, "step": 1}
    )

    # Mappa step → list di (provider, op_type, units, sub_type)
    STEP_COST_MODEL = {
        "claude_master_copy":   [("claude", "sonnet-4.5", 1, None, 4500, 3500)],   # tokens_in/out estimate
        "perplexity_faq":       [("perplexity", "sonar-pro", 1, "request", 0, 0)],
        "perplexity_geo":       [("perplexity", "sonar", 1, "request", 0, 0)],
        "deepl_translate":      [("deepl", "translate", 6000, "char", 0, 0)],
        "gemini_schema":        [("gemini", "3-pro", 1, None, 2000, 4000)],
        "image_generation":     [("gemini", "nano-banana-2", 1, "image", 0, 0)],
    }

    inserted = 0
    cleared_existing = await db.api_usage_logs.count_documents({"_backfilled": True})
    if cleared_existing > 0:
        await db.api_usage_logs.delete_many({"_backfilled": True})

    async for job in cursor:
        ts = job.get("completed_at") or job.get("created_at") or datetime.now(timezone.utc)
        for step_name, ops in STEP_COST_MODEL.items():
            for (prov, op, units, sub, t_in, t_out) in ops:
                # Compute cost
                if prov in ("claude", "gemini") and "image" not in (sub or ""):
                    p_in = await get_pricing(prov, op, "input")
                    p_out = await get_pricing(prov, op, "output")
                    cost = compute_cost(p_in, t_in / 1000.0) + compute_cost(p_out, t_out / 1000.0)
                else:
                    p = await get_pricing(prov, op, sub)
                    cost = compute_cost(p, units)
                doc = {
                    "provider": prov, "op_type": op, "sub_type": sub,
                    "ts": ts, "status": "ok", "error_code": None, "error_msg": None,
                    "latency_ms": 0, "cost_usd": round(cost, 6),
                    "units_used": units, "tokens_in": t_in, "tokens_out": t_out,
                    "entity_type": job.get("target_type"), "entity_slug": job.get("target_id"),
                    "job_id": str(job["_id"]),
                    "function": f"backfill:{step_name}",
                    "_backfilled": True,
                }
                await db.api_usage_logs.insert_one(doc)
                inserted += 1
    return {
        "ok": True, "logs_inserted": inserted,
        "previously_cleared": cleared_existing,
        "since": since.isoformat(),
    }
