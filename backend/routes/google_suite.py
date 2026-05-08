"""Google APIs Suite — unified routes.

Sub-prefixes:
- /api/google/search-console/*
- /api/google/indexing/*
- /api/google/analytics/*
- /api/google/pagespeed/*
"""
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends, Query

from routes.admin_auth import verify_admin_token
from services import (google_analytics_ga4, google_indexing, google_pagespeed,
                      google_search_console)
from services.google_common import get_service_account_email, is_configured

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/google", tags=["google-suite"])


@router.get("/status")
async def status(_=Depends(verify_admin_token)) -> Dict[str, Any]:
    """Quick health check: SA file present + email."""
    return {
        "configured": is_configured(),
        "service_account_email": get_service_account_email(),
        "setup_steps": {
            "search_console": "Add the SA email as Owner in Search Console → Settings → Users and permissions",
            "ga4": "Add the SA email as Viewer in GA4 → Admin → Property → Property access management",
            "indexing": "Same as Search Console (requires Owner permission)",
            "pagespeed": "Already enabled, no per-property linking needed",
        },
    }


# ============================ Search Console ============================
@router.get("/search-console/sites")
async def sc_sites(_=Depends(verify_admin_token)):
    return await google_search_console.list_sites()


@router.get("/search-console/queries")
async def sc_queries(
    site_url: str = Query(..., description="Site URL as registered in Search Console"),
    days: int = Query(28, ge=1, le=90),
    limit: int = Query(100, ge=1, le=500),
    _=Depends(verify_admin_token),
):
    return await google_search_console.top_queries(site_url, days=days, limit=limit)


@router.get("/search-console/pages")
async def sc_pages(
    site_url: str = Query(...),
    days: int = Query(28, ge=1, le=90),
    limit: int = Query(100, ge=1, le=500),
    _=Depends(verify_admin_token),
):
    return await google_search_console.top_pages(site_url, days=days, limit=limit)


@router.get("/search-console/opportunities")
async def sc_opportunities(
    site_url: str = Query(...),
    days: int = Query(28, ge=1, le=90),
    min_pos: float = Query(11.0),
    max_pos: float = Query(20.0),
    min_impressions: int = Query(50, ge=0),
    limit: int = Query(100, ge=1, le=500),
    _=Depends(verify_admin_token),
):
    return await google_search_console.opportunities(
        site_url, days=days, min_pos=min_pos, max_pos=max_pos,
        min_impressions=min_impressions, limit=limit,
    )


# =============================== Indexing ===============================
@router.post("/indexing/submit")
async def idx_submit(
    body: Dict[str, Any] = Body(..., example={"url": "https://golevents.com/...", "action": "URL_UPDATED"}),
    _=Depends(verify_admin_token),
):
    url = body.get("url")
    action = body.get("action", "URL_UPDATED")
    if not url:
        return {"ok": False, "error": "url_required"}
    return await google_indexing.submit_url(url, action=action)


@router.post("/indexing/submit-batch")
async def idx_submit_batch(
    body: Dict[str, Any] = Body(..., example={"urls": ["https://golevents.com/..."], "action": "URL_UPDATED"}),
    _=Depends(verify_admin_token),
):
    urls = body.get("urls") or []
    action = body.get("action", "URL_UPDATED")
    if not urls:
        return {"ok": False, "error": "urls_required"}
    return await google_indexing.submit_batch(urls, action=action)


@router.get("/indexing/metadata")
async def idx_metadata(url: str = Query(...), _=Depends(verify_admin_token)):
    return await google_indexing.get_metadata(url)


@router.get("/indexing/history")
async def idx_history(limit: int = Query(100, ge=1, le=500), _=Depends(verify_admin_token)):
    return await google_indexing.history(limit=limit)


# =============================== Analytics ==============================
@router.get("/analytics/properties")
async def ga_properties(_=Depends(verify_admin_token)):
    return await google_analytics_ga4.list_properties()


@router.get("/analytics/overview")
async def ga_overview(
    property_id: str = Query(..., description="Format: 'properties/123456' or just '123456'"),
    days: int = Query(7, ge=1, le=90),
    _=Depends(verify_admin_token),
):
    return await google_analytics_ga4.overview(property_id, days=days)


@router.get("/analytics/top-pages")
async def ga_top_pages(
    property_id: str = Query(...),
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(20, ge=1, le=100),
    _=Depends(verify_admin_token),
):
    return await google_analytics_ga4.top_pages(property_id, days=days, limit=limit)


@router.get("/analytics/sources")
async def ga_sources(
    property_id: str = Query(...),
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(10, ge=1, le=50),
    _=Depends(verify_admin_token),
):
    return await google_analytics_ga4.traffic_sources(property_id, days=days, limit=limit)


@router.get("/analytics/daily")
async def ga_daily(
    property_id: str = Query(...),
    days: int = Query(28, ge=1, le=90),
    _=Depends(verify_admin_token),
):
    return await google_analytics_ga4.daily_users(property_id, days=days)


# =============================== PageSpeed ==============================
@router.post("/pagespeed/scan")
async def ps_scan(
    body: Dict[str, Any] = Body(..., example={"url": "https://golevents.com", "strategy": "mobile"}),
    _=Depends(verify_admin_token),
):
    url = body.get("url")
    strategy = body.get("strategy", "mobile")
    if not url:
        return {"ok": False, "error": "url_required"}
    return await google_pagespeed.scan(url, strategy=strategy)


@router.post("/pagespeed/scan-batch")
async def ps_scan_batch(
    body: Dict[str, Any] = Body(..., example={"urls": ["https://golevents.com"], "strategy": "mobile"}),
    _=Depends(verify_admin_token),
):
    urls = body.get("urls") or []
    strategy = body.get("strategy", "mobile")
    if not urls:
        return {"ok": False, "error": "urls_required"}
    return await google_pagespeed.scan_batch(urls, strategy=strategy)


@router.get("/pagespeed/dashboard")
async def ps_dashboard(limit: int = Query(20, ge=1, le=100), _=Depends(verify_admin_token)):
    return await google_pagespeed.latest_dashboard(limit=limit)


@router.get("/pagespeed/history")
async def ps_history(
    url: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    _=Depends(verify_admin_token),
):
    return await google_pagespeed.history(url=url, limit=limit)
