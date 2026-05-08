"""Google PageSpeed Insights API integration.

Free up to 25k queries/day per IP. Returns Core Web Vitals + Lighthouse score.
Stores history in db.pagespeed_scans for trend analysis.
"""
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from database import db
from services.api_cost_tracker import track_api_usage

logger = logging.getLogger(__name__)

PAGESPEED_API_KEY = os.environ.get("PAGESPEED_API_KEY")  # optional, raises quota
PAGESPEED_URL = "https://pagespeedonline.googleapis.com/pagespeedonline/v5/runPagespeed"


def _extract_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract LCP/CLS/TBT/FCP/SI/TTI + perf score from raw lighthouse JSON."""
    lh = data.get("lighthouseResult", {})
    cats = lh.get("categories", {})
    audits = lh.get("audits", {})
    perf_score = cats.get("performance", {}).get("score")
    perf = int(perf_score * 100) if perf_score is not None else None
    seo_score = cats.get("seo", {}).get("score")
    a11y_score = cats.get("accessibility", {}).get("score")
    bp_score = cats.get("best-practices", {}).get("score")

    def _audit(key: str) -> Optional[Dict[str, Any]]:
        a = audits.get(key)
        if not a:
            return None
        return {
            "value": a.get("numericValue"),
            "display": a.get("displayValue"),
            "score": a.get("score"),
        }

    return {
        "performance_score": perf,
        "seo_score": int(seo_score * 100) if seo_score is not None else None,
        "accessibility_score": int(a11y_score * 100) if a11y_score is not None else None,
        "best_practices_score": int(bp_score * 100) if bp_score is not None else None,
        "lcp": _audit("largest-contentful-paint"),
        "fcp": _audit("first-contentful-paint"),
        "cls": _audit("cumulative-layout-shift"),
        "tbt": _audit("total-blocking-time"),
        "speed_index": _audit("speed-index"),
        "tti": _audit("interactive"),
    }


@track_api_usage("google_pagespeed", "scan")
async def scan(url: str, strategy: str = "mobile") -> Dict[str, Any]:
    """Run a PageSpeed scan. strategy: 'mobile' or 'desktop'."""
    params = {"url": url, "strategy": strategy, "category": ["performance", "seo", "accessibility", "best-practices"]}
    if PAGESPEED_API_KEY:
        params["key"] = PAGESPEED_API_KEY
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.get(PAGESPEED_URL, params=params)
        if r.status_code != 200:
            return {"ok": False, "url": url, "strategy": strategy,
                    "status_code": r.status_code,
                    "error": (r.json().get("error", {}).get("message") if r.content else "unknown")[:300]}
        data = r.json()
        metrics = _extract_metrics(data)
        record = {
            "url": url, "strategy": strategy,
            **metrics,
            "scanned_at": datetime.now(timezone.utc),
        }
        await db.pagespeed_scans.insert_one(record)
        return {"ok": True, "url": url, "strategy": strategy, **metrics, "scanned_at": record["scanned_at"].isoformat()}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e)[:300]}


async def scan_batch(urls: List[str], strategy: str = "mobile") -> Dict[str, Any]:
    """Sequential scan. Each takes ~30-60s, so be patient."""
    out = []
    for u in urls[:50]:
        r = await scan(u, strategy=strategy)
        out.append(r)
    success = [x for x in out if x.get("ok")]
    failed = [x for x in out if not x.get("ok")]
    return {"results": out, "success_count": len(success), "failed_count": len(failed)}


async def history(url: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
    """Last scans. Filter by URL if provided."""
    q = {"url": url} if url else {}
    rows = await db.pagespeed_scans.find(q, {"_id": 0}).sort("scanned_at", -1).limit(limit).to_list(limit)
    for r in rows:
        if isinstance(r.get("scanned_at"), datetime):
            r["scanned_at"] = r["scanned_at"].isoformat()
    return {"rows": rows, "total": len(rows)}


async def latest_dashboard(limit: int = 20) -> Dict[str, Any]:
    """Latest scan per URL (for dashboard table)."""
    pipeline = [
        {"$sort": {"scanned_at": -1}},
        {"$group": {
            "_id": {"url": "$url", "strategy": "$strategy"},
            "doc": {"$first": "$$ROOT"},
        }},
        {"$replaceRoot": {"newRoot": "$doc"}},
        {"$sort": {"performance_score": 1}},  # worst first
        {"$limit": limit},
    ]
    rows = await db.pagespeed_scans.aggregate(pipeline).to_list(limit)
    out = []
    for r in rows:
        r.pop("_id", None)
        if isinstance(r.get("scanned_at"), datetime):
            r["scanned_at"] = r["scanned_at"].isoformat()
        out.append(r)
    return {"rows": out, "total": len(out)}
