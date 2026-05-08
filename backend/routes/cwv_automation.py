"""CWV Automation routes — scan/auto-fix/patch/track."""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Body, Depends, Query

from database import db
from routes.admin_auth import verify_admin_token
from services import cwv_html_analyzer, cwv_image_optimizer, cwv_patch_generator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/seo/cwv", tags=["seo-cwv-automation"])


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ============================ Scan ============================
@router.post("/scan")
async def scan(body: Dict[str, Any] = Body(...), _=Depends(verify_admin_token)):
    """Run analyzer on a URL. Persists scan in DB."""
    url = (body.get("url") or "").strip()
    if not url:
        return {"ok": False, "error": "url required"}
    result = await cwv_html_analyzer.analyze_url(url)
    if not result.get("ok"):
        return result
    scan_id = uuid.uuid4().hex[:12]
    await db.cwv_scans.insert_one({
        "_scan_id": scan_id,
        "url": url,
        "ts": _now(),
        "score": result["score"],
        "detected_count": result["detected_count"],
        "items": result["items"],
        "bonus": result.get("bonus", {}),
        "total_imgs": result.get("total_imgs"),
        "total_scripts": result.get("total_scripts"),
        "html_size": result.get("html_size"),
    })
    # Initialize action statuses for all CWV items found as detected
    for item in result["items"]:
        existing = await db.cwv_actions.find_one({"target_url": url, "cwv_id": item["id"]})
        if existing:
            continue
        await db.cwv_actions.insert_one({
            "target_url": url,
            "cwv_id": item["id"],
            "title": item["title"],
            "kind": item["kind"],   # 'auto' or 'manual'
            "tier": item["tier"],
            "category": item["category"],
            "status": "TODO" if item.get("detected") else "OK",
            "last_scan_id": scan_id,
            "last_scan_ts": _now(),
            "created_at": _now(),
            "updated_at": _now(),
        })
    return {"ok": True, "scan_id": scan_id, **result}


@router.get("/scans")
async def list_scans(
    url: Optional[str] = Query(None),
    limit: int = Query(30, ge=1, le=100),
    _=Depends(verify_admin_token),
):
    q = {"url": url} if url else {}
    rows = await db.cwv_scans.find(q, {"_id": 0, "items": 0, "bonus": 0}).sort("ts", -1).limit(limit).to_list(limit)
    for r in rows:
        if isinstance(r.get("ts"), datetime):
            r["ts"] = r["ts"].isoformat()
    return {"rows": rows, "total": len(rows)}


@router.get("/scan/{scan_id}")
async def scan_detail(scan_id: str, _=Depends(verify_admin_token)):
    doc = await db.cwv_scans.find_one({"_scan_id": scan_id}, {"_id": 0})
    if not doc:
        return {"ok": False, "error": "not_found"}
    if isinstance(doc.get("ts"), datetime):
        doc["ts"] = doc["ts"].isoformat()
    return {"ok": True, **doc}


# ============================ Actions status ============================
@router.get("/actions")
async def list_actions(
    target_url: str = Query(...),
    _=Depends(verify_admin_token),
):
    rows = await db.cwv_actions.find({"target_url": target_url}, {"_id": 0}).sort("cwv_id", 1).to_list(50)
    for r in rows:
        for k in ("created_at", "updated_at", "last_scan_ts", "applied_at", "generated_at"):
            v = r.get(k)
            if isinstance(v, datetime):
                r[k] = v.isoformat()
    return {"rows": rows}


# ============================ Auto-fix actions ============================
@router.post("/auto-fix/{cwv_id}")
async def auto_fix(cwv_id: str, body: Optional[Dict[str, Any]] = Body(None),
                   _=Depends(verify_admin_token)):
    """Execute the auto-fix for a CWV. Currently supports: CWV-1, CWV-5, CWV-6, CWV-11."""
    body = body or {}
    target_url = (body.get("target_url") or "").strip()

    result: Dict[str, Any] = {"ok": False}
    if cwv_id == "CWV-1":
        # Hero image WebP/AVIF batch convert
        folder = body.get("folder") or "/app/backend/uploads/seo"
        result = cwv_image_optimizer.batch_convert(folder)
        result["ok"] = bool(result.get("ok"))
        result["message"] = (f"Converted {result.get('success',0)} images. "
                             f"WebP saved {result.get('saving_webp_pct',0)}%, "
                             f"AVIF saved {result.get('saving_avif_pct',0)}%.")
    elif cwv_id == "CWV-5":
        # PageSpeed weekly cron — already enabled via scheduler.py
        result = {"ok": True, "message": "PageSpeed weekly scheduler is already active (Sunday 06:00 UTC). "
                                         "Verify in /admin/seo/google-suite > PageSpeed tab."}
    elif cwv_id == "CWV-6":
        # SSR JSON-LD via prerender — already in /api/prerender/* on golevents
        result = {"ok": True, "message": "SSR JSON-LD prerender is enabled in this module via "
                                         "routes/prerender.py. Wire to your reverse-proxy "
                                         "(nginx) to serve bots from /api/prerender/event/<slug>."}
    elif cwv_id == "CWV-11":
        # Critical CSS extraction — point user to a build-time tool
        result = {"ok": True, "message": "Critical CSS extraction is a build-time step. Add "
                                         "'critters' or 'penthouse' to your Webpack/Vite config "
                                         "to inline above-the-fold CSS automatically."}
    else:
        return {"ok": False, "error": f"{cwv_id} has no auto-fix (manual patch required)"}

    if target_url:
        await db.cwv_actions.update_one(
            {"target_url": target_url, "cwv_id": cwv_id},
            {"$set": {
                "status": "DONE",
                "applied_at": _now(),
                "updated_at": _now(),
                "last_result": {k: v for k, v in result.items() if k != "details"},
            }},
        )
    return result


@router.post("/auto-fix-all")
async def auto_fix_all(body: Dict[str, Any] = Body(...), _=Depends(verify_admin_token)):
    target_url = body.get("target_url", "")
    out = {}
    for cwv in ("CWV-1", "CWV-5", "CWV-6", "CWV-11"):
        r = await auto_fix(cwv, {"target_url": target_url})
        out[cwv] = r
    return {"ok": True, "results": out}


# ============================ Manual patch generation ============================
@router.get("/patch/{cwv_id}")
async def patch_get(cwv_id: str, target_url: Optional[str] = Query(None),
                    _=Depends(verify_admin_token)):
    p = cwv_patch_generator.generate_patch(cwv_id)
    if not p.get("ok"):
        return p
    if target_url:
        await db.cwv_actions.update_one(
            {"target_url": target_url, "cwv_id": cwv_id},
            {"$set": {
                "status": "GENERATED",
                "generated_at": _now(),
                "updated_at": _now(),
            }},
        )
    return p


@router.post("/mark-applied")
async def mark_applied(body: Dict[str, Any] = Body(...), _=Depends(verify_admin_token)):
    target_url = body["target_url"]
    cwv_id = body["cwv_id"]
    res = await db.cwv_actions.update_one(
        {"target_url": target_url, "cwv_id": cwv_id},
        {"$set": {"status": "DONE", "applied_at": _now(), "updated_at": _now()}},
    )
    return {"ok": True, "modified": res.modified_count}


@router.post("/reset-action")
async def reset_action(body: Dict[str, Any] = Body(...), _=Depends(verify_admin_token)):
    target_url = body["target_url"]
    cwv_id = body["cwv_id"]
    res = await db.cwv_actions.update_one(
        {"target_url": target_url, "cwv_id": cwv_id},
        {"$set": {"status": "TODO", "updated_at": _now()},
         "$unset": {"applied_at": "", "generated_at": ""}},
    )
    return {"ok": True, "modified": res.modified_count}


# ============================ Score history ============================
@router.get("/score-history")
async def score_history(
    url: str = Query(...),
    days: int = Query(90, ge=1, le=365),
    _=Depends(verify_admin_token),
):
    from datetime import timedelta
    since = _now() - timedelta(days=days)
    rows = await db.cwv_scans.find(
        {"url": url, "ts": {"$gte": since}},
        {"_id": 0, "ts": 1, "score": 1, "detected_count": 1},
    ).sort("ts", 1).to_list(500)
    for r in rows:
        if isinstance(r.get("ts"), datetime):
            r["ts"] = r["ts"].isoformat()
    return {"rows": rows}
