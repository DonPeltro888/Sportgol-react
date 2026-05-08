"""
Cost Observatory routes — /api/seo/cost-observatory/*

Endpoints:
- GET  /overview                  → top stats
- GET  /chart/daily?days=30       → time-series spesa
- GET  /providers                 → per-provider breakdown
- GET  /entities/top?days=30      → top expensive entities
- GET  /entities/by-type          → cost per type (event/team/league)
- GET  /logs?provider=&status=    → drill-down logs
- GET  /latency?days=7            → p50/p95 per provider
- GET  /pricing                   → list all pricing
- POST /pricing                   → override pricing
- GET  /budgets                   → list all budgets
- POST /budgets/{provider}        → set budget for provider
- GET  /alerts/open               → open alerts
- POST /alerts/{id}/ack           → acknowledge alert
- POST /alerts/run-checks         → manual trigger
- GET  /balance                   → balance (real + estimated)
- POST /backfill?days=30          → backfill from seo_jobs
- GET  /alert-config              → email/SMTP config
- POST /alert-config              → save config
- GET  /export?format=csv         → export CSV
"""
import csv
import io
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from database import db
from routes.admin_auth import verify_admin_token
from services import api_cost_observatory as obs
from services import api_pricing, api_balance_checker, api_alerts

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/seo/cost-observatory", tags=["cost-observatory"])


# ============= Overview / Stats =============

@router.get("/overview")
async def get_overview(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    return await obs.overview_stats()


@router.get("/chart/daily")
async def get_chart_daily(days: int = Query(30, ge=1, le=90), _=Depends(verify_admin_token)):
    return {"rows": await obs.daily_chart(days=days)}


@router.get("/providers")
async def get_providers(_=Depends(verify_admin_token)):
    return {"rows": await obs.by_provider()}


@router.get("/entities/top")
async def get_top_entities(days: int = 30, limit: int = 10, _=Depends(verify_admin_token)):
    return {"rows": await obs.top_expensive_entities(days=days, limit=limit)}


@router.get("/entities/by-type")
async def get_by_entity_type(days: int = 30, _=Depends(verify_admin_token)):
    return {"rows": await obs.by_entity_type(days=days)}


@router.get("/logs")
async def get_logs(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    provider: Optional[str] = None,
    status: Optional[str] = None,
    entity_slug: Optional[str] = None,
    error_code: Optional[str] = None,
    _=Depends(verify_admin_token),
):
    return await obs.list_logs(limit=limit, offset=offset, provider=provider,
                                status=status, entity_slug=entity_slug, error_code=error_code)


@router.get("/latency")
async def get_latency(provider: Optional[str] = None, days: int = 7, _=Depends(verify_admin_token)):
    return await obs.latency_distribution(provider=provider, days=days)


# ============= Pricing =============

@router.get("/pricing")
async def get_pricing_list(_=Depends(verify_admin_token)):
    return await api_pricing.list_all_pricing()


class PricingOverride(BaseModel):
    provider: str
    op_type: str
    sub_type: Optional[str] = None
    cost_per_unit: float = Field(..., ge=0)
    unit: Optional[str] = None
    note: Optional[str] = None


@router.post("/pricing")
async def set_pricing_override(payload: PricingOverride, _=Depends(verify_admin_token)):
    doc = await api_pricing.set_pricing(
        payload.provider, payload.op_type, payload.sub_type,
        payload.cost_per_unit, payload.unit, payload.note,
    )
    return {"ok": True, "doc": {k: v for k, v in doc.items() if k != "updated_at"}}


# ============= Budgets =============

@router.get("/budgets")
async def get_budgets(_=Depends(verify_admin_token)):
    rows = []
    async for d in db.api_budgets.find({}, {"_id": 1, "monthly_limit_usd": 1, "warning_pct": 1}):
        rows.append({
            "provider": d["_id"],
            "monthly_limit_usd": d.get("monthly_limit_usd"),
            "warning_pct": d.get("warning_pct", 80),
        })
    return {"rows": rows}


class BudgetSet(BaseModel):
    monthly_limit_usd: float = Field(..., ge=0)
    warning_pct: float = Field(80, ge=10, le=100)


@router.post("/budgets/{provider}")
async def set_budget(provider: str, payload: BudgetSet, _=Depends(verify_admin_token)):
    await db.api_budgets.update_one(
        {"_id": provider},
        {"$set": {"monthly_limit_usd": payload.monthly_limit_usd,
                  "warning_pct": payload.warning_pct,
                  "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )
    return {"ok": True, "provider": provider, "monthly_limit_usd": payload.monthly_limit_usd}


@router.delete("/budgets/{provider}")
async def delete_budget(provider: str, _=Depends(verify_admin_token)):
    await db.api_budgets.delete_one({"_id": provider})
    return {"ok": True}


# ============= Alerts =============

@router.get("/alerts/open")
async def get_open_alerts(_=Depends(verify_admin_token)):
    items = await api_alerts.list_open_alerts(limit=100)
    out = []
    for it in items:
        if isinstance(it.get("ts"), datetime):
            it["ts"] = it["ts"].isoformat()
        if it.get("ack_at") and isinstance(it["ack_at"], datetime):
            it["ack_at"] = it["ack_at"].isoformat()
        out.append(it)
    return {"items": out, "count": len(out)}


@router.post("/alerts/{alert_id}/ack")
async def ack_alert(alert_id: str, _=Depends(verify_admin_token)):
    ok = await api_alerts.acknowledge_alert(alert_id)
    return {"ok": ok}


@router.post("/alerts/ack-all/{provider}")
async def ack_all_provider(provider: str, _=Depends(verify_admin_token)):
    n = await api_alerts.acknowledge_all_for_provider(provider)
    return {"ok": True, "ack_count": n}


@router.post("/alerts/run-checks")
async def run_alert_checks(_=Depends(verify_admin_token)):
    return await api_alerts.run_all_alert_checks()


# ============= Balance =============

@router.get("/balance")
async def get_balance(_=Depends(verify_admin_token)):
    return await api_balance_checker.snapshot_all_balances()


# ============= Backfill =============

@router.post("/backfill")
async def backfill(days: int = Query(30, ge=1, le=90), _=Depends(verify_admin_token)):
    return await obs.backfill_from_seo_jobs(days=days)


# ============= Alert Config (Resend / SMTP) =============

class AlertConfig(BaseModel):
    email_enabled: bool = True
    from_email: Optional[str] = None
    to_email: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = 465
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    email_on_budget_warning: bool = True
    email_on_budget_exceeded: bool = True
    email_on_low_balance: bool = True
    email_on_api_down: bool = True
    email_on_api_intermittent: bool = False


@router.get("/alert-config")
async def get_alert_config(_=Depends(verify_admin_token)):
    cfg = await db.alert_config.find_one({"_id": "main"}, {"_id": 0}) or {}
    # Hide smtp_pass for security (just show if set)
    has_smtp_pass = bool(cfg.get("smtp_pass"))
    cfg.pop("smtp_pass", None)
    cfg["smtp_pass_set"] = has_smtp_pass
    # Check resend key configured
    from services.seo_keys import get_api_key
    cfg["resend_key_set"] = bool(await get_api_key("resend"))
    return cfg


@router.post("/alert-config")
async def save_alert_config(payload: AlertConfig, _=Depends(verify_admin_token)):
    doc = payload.dict(exclude_none=True)
    doc["updated_at"] = datetime.now(timezone.utc)
    # Don't overwrite smtp_pass if not provided
    if not payload.smtp_pass:
        doc.pop("smtp_pass", None)
    await db.alert_config.update_one({"_id": "main"}, {"$set": doc}, upsert=True)
    return {"ok": True}


# ============= Export =============

@router.get("/export")
async def export_csv(
    days: int = Query(30, ge=1, le=365),
    provider: Optional[str] = None,
    _=Depends(verify_admin_token),
):
    from datetime import timedelta
    since = datetime.now(timezone.utc) - timedelta(days=days)
    flt: Dict[str, Any] = {"ts": {"$gte": since}}
    if provider:
        flt["provider"] = provider

    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["ts", "provider", "op_type", "sub_type", "status", "error_code",
                "latency_ms", "cost_usd", "tokens_in", "tokens_out", "units_used",
                "entity_type", "entity_slug", "job_id", "function"])
    cursor = db.api_usage_logs.find(flt, {"_id": 0}).sort("ts", -1)
    async for d in cursor:
        ts = d.get("ts")
        if isinstance(ts, datetime):
            ts = ts.isoformat()
        w.writerow([ts, d.get("provider"), d.get("op_type"), d.get("sub_type"),
                    d.get("status"), d.get("error_code"), d.get("latency_ms"),
                    d.get("cost_usd"), d.get("tokens_in"), d.get("tokens_out"),
                    d.get("units_used"), d.get("entity_type"), d.get("entity_slug"),
                    d.get("job_id"), d.get("function")])
    output.seek(0)
    fname = f"api-usage-{datetime.now().strftime('%Y%m%d')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={fname}"},
    )
