"""Google Search Console API integration.

Tracks: top queries (keywords), top pages, opportunities (pos 11-20), drift.
"""
import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from services.api_cost_tracker import track_api_usage
from services.google_common import load_credentials

logger = logging.getLogger(__name__)

SCOPES = ("https://www.googleapis.com/auth/webmasters.readonly",)


def _client():
    creds = load_credentials(SCOPES)
    if not creds:
        return None
    return build("searchconsole", "v1", credentials=creds, cache_discovery=False)


@track_api_usage("google_search_console", "sites_list")
async def list_sites() -> Dict[str, Any]:
    sc = _client()
    if not sc:
        return {"sites": [], "error": "service_account_not_configured"}
    try:
        r = sc.sites().list().execute()
        return {"sites": r.get("siteEntry", [])}
    except HttpError as e:
        return {"sites": [], "error": e._get_reason()}


def _date_range(days: int = 28) -> tuple:
    end = date.today() - timedelta(days=2)  # GSC has ~2-day lag
    start = end - timedelta(days=days)
    return start.isoformat(), end.isoformat()


@track_api_usage("google_search_console", "query")
async def query_performance(
    site_url: str,
    *,
    days: int = 28,
    dimensions: Optional[List[str]] = None,
    row_limit: int = 100,
    start_row: int = 0,
) -> Dict[str, Any]:
    """Generic query helper. dimensions can be ['query'], ['page'], ['query','page']."""
    sc = _client()
    if not sc:
        return {"rows": [], "error": "service_account_not_configured"}
    start, end = _date_range(days)
    try:
        body = {
            "startDate": start,
            "endDate": end,
            "dimensions": dimensions or ["query"],
            "rowLimit": min(row_limit, 1000),
            "startRow": start_row,
        }
        r = sc.searchanalytics().query(siteUrl=site_url, body=body).execute()
        return {
            "site_url": site_url,
            "start_date": start,
            "end_date": end,
            "rows": r.get("rows", []),
        }
    except HttpError as e:
        return {"rows": [], "error": e._get_reason()}


async def top_queries(site_url: str, days: int = 28, limit: int = 100) -> Dict[str, Any]:
    return await query_performance(site_url, days=days, dimensions=["query"], row_limit=limit)


async def top_pages(site_url: str, days: int = 28, limit: int = 100) -> Dict[str, Any]:
    return await query_performance(site_url, days=days, dimensions=["page"], row_limit=limit)


async def opportunities(
    site_url: str, days: int = 28, min_pos: float = 11.0, max_pos: float = 20.0,
    min_impressions: int = 50, limit: int = 100,
) -> Dict[str, Any]:
    """Find queries on positions 11-20 (page 2) that need a small push to reach page 1."""
    raw = await query_performance(site_url, days=days, dimensions=["query"], row_limit=1000)
    if "error" in raw and not raw.get("rows"):
        return raw
    out = []
    for r in raw.get("rows", []):
        pos = r.get("position", 0)
        imps = r.get("impressions", 0)
        if min_pos <= pos <= max_pos and imps >= min_impressions:
            out.append({
                "query": (r.get("keys") or [""])[0],
                "clicks": r.get("clicks", 0),
                "impressions": imps,
                "ctr": round(r.get("ctr", 0) * 100, 2),
                "position": round(pos, 1),
                "potential_clicks": int(imps * 0.10),  # rough estimate at pos 5-10
            })
    out.sort(key=lambda x: x["impressions"], reverse=True)
    return {
        "site_url": site_url,
        "start_date": raw.get("start_date"),
        "end_date": raw.get("end_date"),
        "rows": out[:limit],
    }
