"""Google Analytics 4 (GA4) Data API integration.

Reads users, sessions, top pages, traffic sources, conversions.
"""
import logging
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from services.api_cost_tracker import track_api_usage
from services.google_common import load_credentials

logger = logging.getLogger(__name__)

SCOPES = ("https://www.googleapis.com/auth/analytics.readonly",)


def _admin_client():
    creds = load_credentials(SCOPES)
    if not creds:
        return None
    return build("analyticsadmin", "v1beta", credentials=creds, cache_discovery=False)


def _data_client():
    creds = load_credentials(SCOPES)
    if not creds:
        return None
    return build("analyticsdata", "v1beta", credentials=creds, cache_discovery=False)


@track_api_usage("google_analytics", "list_properties")
async def list_properties() -> Dict[str, Any]:
    admin = _admin_client()
    if not admin:
        return {"properties": [], "error": "service_account_not_configured"}
    try:
        r = admin.accountSummaries().list().execute()
        out = []
        for a in r.get("accountSummaries", []):
            for p in a.get("propertySummaries", []):
                out.append({
                    "account": a.get("displayName"),
                    "property_name": p.get("displayName"),
                    "property_id": p.get("property"),  # "properties/123456"
                    "property_short_id": (p.get("property") or "").replace("properties/", ""),
                })
        return {"properties": out}
    except HttpError as e:
        return {"properties": [], "error": e._get_reason()}


def _run_report(property_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """Internal: run a GA4 Data API report."""
    data = _data_client()
    if not data:
        return {"error": "service_account_not_configured"}
    pid = property_id if property_id.startswith("properties/") else f"properties/{property_id}"
    try:
        return data.properties().runReport(property=pid, body=body).execute()
    except HttpError as e:
        return {"error": e._get_reason()}


@track_api_usage("google_analytics", "overview")
async def overview(property_id: str, days: int = 7) -> Dict[str, Any]:
    body = {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
        "metrics": [
            {"name": "activeUsers"},
            {"name": "sessions"},
            {"name": "screenPageViews"},
            {"name": "averageSessionDuration"},
            {"name": "bounceRate"},
            {"name": "conversions"},
        ],
    }
    r = _run_report(property_id, body)
    if "error" in r:
        return r
    rows = r.get("rows", [])
    if not rows:
        return {"users": 0, "sessions": 0, "page_views": 0,
                "avg_session_duration": 0, "bounce_rate": 0, "conversions": 0}
    vals = rows[0].get("metricValues", [])
    return {
        "users": int(vals[0]["value"]) if len(vals) > 0 else 0,
        "sessions": int(vals[1]["value"]) if len(vals) > 1 else 0,
        "page_views": int(vals[2]["value"]) if len(vals) > 2 else 0,
        "avg_session_duration": round(float(vals[3]["value"]), 1) if len(vals) > 3 else 0,
        "bounce_rate": round(float(vals[4]["value"]) * 100, 2) if len(vals) > 4 else 0,
        "conversions": int(float(vals[5]["value"])) if len(vals) > 5 else 0,
        "days": days,
    }


@track_api_usage("google_analytics", "top_pages")
async def top_pages(property_id: str, days: int = 7, limit: int = 20) -> Dict[str, Any]:
    body = {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "pagePath"}, {"name": "pageTitle"}],
        "metrics": [{"name": "screenPageViews"}, {"name": "activeUsers"}],
        "orderBys": [{"metric": {"metricName": "screenPageViews"}, "desc": True}],
        "limit": limit,
    }
    r = _run_report(property_id, body)
    if "error" in r:
        return r
    out = []
    for row in r.get("rows", []):
        d = row.get("dimensionValues", [])
        m = row.get("metricValues", [])
        out.append({
            "path": d[0]["value"] if len(d) > 0 else "",
            "title": d[1]["value"] if len(d) > 1 else "",
            "page_views": int(m[0]["value"]) if len(m) > 0 else 0,
            "users": int(m[1]["value"]) if len(m) > 1 else 0,
        })
    return {"rows": out, "days": days}


@track_api_usage("google_analytics", "sources")
async def traffic_sources(property_id: str, days: int = 7, limit: int = 10) -> Dict[str, Any]:
    body = {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "sessionDefaultChannelGroup"}, {"name": "sessionSource"}],
        "metrics": [{"name": "sessions"}, {"name": "activeUsers"}],
        "orderBys": [{"metric": {"metricName": "sessions"}, "desc": True}],
        "limit": limit,
    }
    r = _run_report(property_id, body)
    if "error" in r:
        return r
    out = []
    for row in r.get("rows", []):
        d = row.get("dimensionValues", [])
        m = row.get("metricValues", [])
        out.append({
            "channel": d[0]["value"] if len(d) > 0 else "",
            "source": d[1]["value"] if len(d) > 1 else "",
            "sessions": int(m[0]["value"]) if len(m) > 0 else 0,
            "users": int(m[1]["value"]) if len(m) > 1 else 0,
        })
    return {"rows": out, "days": days}


@track_api_usage("google_analytics", "daily")
async def daily_users(property_id: str, days: int = 28) -> Dict[str, Any]:
    """For chart rendering."""
    body = {
        "dateRanges": [{"startDate": f"{days}daysAgo", "endDate": "today"}],
        "dimensions": [{"name": "date"}],
        "metrics": [{"name": "activeUsers"}, {"name": "sessions"}],
        "orderBys": [{"dimension": {"dimensionName": "date"}}],
    }
    r = _run_report(property_id, body)
    if "error" in r:
        return r
    out = []
    for row in r.get("rows", []):
        d = row.get("dimensionValues", [])
        m = row.get("metricValues", [])
        date_str = d[0]["value"] if len(d) > 0 else ""
        out.append({
            "date": f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}" if len(date_str) == 8 else date_str,
            "users": int(m[0]["value"]) if len(m) > 0 else 0,
            "sessions": int(m[1]["value"]) if len(m) > 1 else 0,
        })
    return {"rows": out, "days": days}
