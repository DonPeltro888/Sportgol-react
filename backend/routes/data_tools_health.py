"""
SEO Health routes — scan + AI fix + report storage + export.
"""
import asyncio
import io
import csv
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from database import db
from routes.admin_auth import verify_admin_token
from services import seo_health_check, seo_health_fix

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/data-tools/health", tags=["data-tools-health"])


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Scan (read-only) ──────────────────────────────────────────────────────

@router.get("/scan")
async def scan(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Esegue scan completo read-only e ritorna il report (non salva)."""
    report = await seo_health_check.full_scan()
    return {"ok": True, "scanned_at": _now_iso(), **report}


@router.post("/run")
async def run_and_save(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Esegue scan e SALVA il report in db.health_reports."""
    report = await seo_health_check.full_scan()
    report_id = str(uuid.uuid4())
    await db.health_reports.insert_one({
        "_id": report_id,
        "scanned_at": _now_iso(),
        **report,
    })
    return {"ok": True, "report_id": report_id, "summary": report["summary"]}


@router.get("/report/latest")
async def latest_report(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    cursor = db.health_reports.find({}).sort("scanned_at", -1).limit(1)
    report: Optional[Dict[str, Any]] = None
    async for r in cursor:
        report = r
    if not report:
        return {"ok": False, "error": "No report yet — run /api/seo/health/run first"}
    return report


@router.get("/reports")
async def list_reports(limit: int = 20, _=Depends(verify_admin_token)) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    async for r in db.health_reports.find({}, {"teams": 0, "events": 0, "leagues": 0}).sort("scanned_at", -1).limit(limit):
        items.append(r)
    return {"items": items, "count": len(items)}


# ─── Fix ───────────────────────────────────────────────────────────────────

class FixRequest(BaseModel):
    mode: str = "balanced"  # balanced | safe


@router.post("/fix-team/{slug}")
async def fix_team_endpoint(
    slug: str,
    payload: Optional[FixRequest] = None,
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    mode = (payload.mode if payload else None) or "balanced"
    return await seo_health_fix.fix_team(slug, mode=mode)


class BulkFixRequest(BaseModel):
    slugs: Optional[List[str]] = None
    mode: str = "balanced"
    only_categories: Optional[List[str]] = None  # filtra issues
    limit: int = 100


# Bulk fix usa job queue async
@router.post("/fix-bulk")
async def fix_bulk_endpoint(
    payload: BulkFixRequest,
    _=Depends(verify_admin_token),
) -> Dict[str, Any]:
    """
    Avvia un job di bulk fix.
    Se payload.slugs è None: prende tutti i team con issue da ultimo report.
    """
    slugs: List[str] = payload.slugs or []
    if not slugs:
        # Pesca dall'ultimo report
        report = await db.health_reports.find_one({}, sort=[("scanned_at", -1)])
        if not report:
            raise HTTPException(400, "No report yet — run /api/seo/health/run first")
        teams_issues = (report.get("teams") or {}).get("issues") or []
        seen = set()
        for it in teams_issues:
            cat = it.get("category", "")
            if payload.only_categories and cat not in payload.only_categories:
                continue
            slug = it.get("team_slug") or (it.get("longer_team", {}) or {}).get("slug") or (it.get("shorter_team", {}) or {}).get("slug")
            if slug and slug not in seen:
                seen.add(slug)
                slugs.append(slug)
                if len(slugs) >= payload.limit:
                    break

    if not slugs:
        return {"ok": True, "queued": 0, "note": "No issues to fix"}

    job_id = str(uuid.uuid4())
    await db.health_jobs.insert_one({
        "_id": job_id,
        "type": "bulk_fix",
        "status": "queued",
        "total": len(slugs),
        "processed": 0,
        "fixed": 0,
        "results": [],
        "mode": payload.mode,
        "started_at": _now_iso(),
    })

    asyncio.create_task(_run_bulk_fix(job_id, slugs, payload.mode))
    return {"ok": True, "job_id": job_id, "queued": len(slugs)}


async def _run_bulk_fix(job_id: str, slugs: List[str], mode: str) -> None:
    fixed = 0
    results: List[Dict[str, Any]] = []
    await db.health_jobs.update_one({"_id": job_id}, {"$set": {"status": "running"}})
    for i, slug in enumerate(slugs):
        try:
            r = await seo_health_fix.fix_team(slug, mode=mode)
            results.append({"slug": slug, "ok": r.get("ok"), "applied": r.get("applied"), "actions": r.get("actions", [])})
            if r.get("applied"):
                fixed += 1
        except Exception as e:
            logger.error(f"bulk fix fail {slug}: {e}")
            results.append({"slug": slug, "ok": False, "error": str(e)[:200]})
        await db.health_jobs.update_one(
            {"_id": job_id},
            {"$set": {"processed": i + 1, "fixed": fixed, "results": results[-30:]}},
        )
    await db.health_jobs.update_one(
        {"_id": job_id},
        {"$set": {"status": "succeeded", "fixed": fixed, "completed_at": _now_iso(), "results": results}},
    )


@router.get("/fix-jobs/{job_id}")
async def get_fix_job(job_id: str, _=Depends(verify_admin_token)) -> Dict[str, Any]:
    doc = await db.health_jobs.find_one({"_id": job_id})
    if not doc:
        raise HTTPException(404, "Job not found")
    return doc


@router.get("/fix-jobs")
async def list_fix_jobs(limit: int = 20, _=Depends(verify_admin_token)) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    async for d in db.health_jobs.find({}, {"results": 0}).sort("started_at", -1).limit(limit):
        items.append(d)
    return {"items": items}


# ─── Export ────────────────────────────────────────────────────────────────

@router.get("/export")
async def export_report(format: str = Query("json"), _=Depends(verify_admin_token)):
    """Esporta l'ultimo report in JSON o CSV."""
    report = await db.health_reports.find_one({}, sort=[("scanned_at", -1)])
    if not report:
        raise HTTPException(404, "No report yet")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"health-report-{timestamp}"

    if format == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=["category", "severity", "details"])
        writer.writeheader()
        for collection_key in ("teams", "events", "leagues"):
            coll = report.get(collection_key, {})
            for it in coll.get("issues", []):
                cat = it.get("category", "")
                sev = it.get("severity", "low")
                details = {k: v for k, v in it.items() if k not in ("category", "severity")}
                writer.writerow({"category": cat, "severity": sev, "details": json.dumps(details, ensure_ascii=False, default=str)})
        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}.csv"'},
        )
    body = json.dumps(report, ensure_ascii=False, default=str, indent=2)
    return StreamingResponse(
        iter([body]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}.json"'},
    )
