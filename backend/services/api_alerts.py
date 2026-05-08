"""
API Alert Engine — analizza usage logs + balance e genera alert.

Tipologie:
- BUDGET_WARNING       → soglia % budget mensile superata (default 80%)
- BUDGET_EXCEEDED      → 100% budget superato (solo warning, NO blocco)
- LOW_BALANCE          → saldo residuo basso (es. DeepL char_left < 50k)
- API_DOWN             → fail consecutivi >= 3 nelle ultime 30min
- API_INTERMITTENT     → failure_rate > 30% nelle ultime 24h

Notification channels:
- Dashboard (sempre, salvato in db.api_alerts con status open/acknowledged)
- Email via Resend (se configurato in db.seo_api_keys con tool_id='resend')

Cron: ogni 30min via APScheduler (vedi scheduler.py).
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

import httpx

from database import db
from services.api_balance_checker import PROVIDERS_TO_CHECK, get_provider_balance
from services.seo_keys import get_api_key

logger = logging.getLogger(__name__)


# Soglia di default
DEFAULT_BUDGET_WARNING_PCT = 80
LOW_BALANCE_THRESHOLDS = {
    "deepl_char_left": 50000,   # 50k char rimanenti
    "remaining_usd": 5.0,        # $5 rimasti
}
API_DOWN_FAIL_COUNT = 3      # 3 fail consecutivi
API_DOWN_WINDOW_MIN = 30
INTERMITTENT_THRESHOLD_PCT = 30


async def _send_email_via_resend(subject: str, html: str) -> bool:
    """Invia email via Resend se configurato."""
    cfg = await db.alert_config.find_one({"_id": "main"}, {"_id": 0}) or {}
    resend_key = await get_api_key("resend")
    from_email = cfg.get("from_email") or "alerts@golevents.com"
    to_email = cfg.get("to_email")
    if not resend_key or not to_email:
        return False

    try:
        async with httpx.AsyncClient(timeout=15) as cx:
            r = await cx.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                json={"from": from_email, "to": [to_email], "subject": subject, "html": html},
            )
        return r.status_code in (200, 201, 202)
    except Exception as e:
        logger.error(f"Resend send error: {e}")
        return False


async def _send_email_via_smtp(subject: str, html: str) -> bool:
    """SMTP fallback (uses cfg in db.alert_config)."""
    cfg = await db.alert_config.find_one({"_id": "main"}, {"_id": 0}) or {}
    if not cfg.get("smtp_host"):
        return False
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = cfg.get("from_email") or cfg.get("smtp_user", "alerts@golevents.com")
        msg["To"] = cfg.get("to_email", "")
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL(cfg["smtp_host"], int(cfg.get("smtp_port", 465))) as s:
            s.login(cfg["smtp_user"], cfg["smtp_pass"])
            s.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"SMTP send error: {e}")
        return False


async def _create_alert(alert_type: str, severity: str, provider: str, title: str,
                        message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
    """Crea alert + invia email. Idempotente: se alert dello stesso type+provider è già 'open' nelle ultime 6h, no-op."""
    now = datetime.now(timezone.utc)
    six_hours_ago = now - timedelta(hours=6)
    existing = await db.api_alerts.find_one({
        "alert_type": alert_type,
        "provider": provider,
        "status": "open",
        "ts": {"$gte": six_hours_ago},
    })
    if existing:
        return {"created": False, "reason": "duplicate_recent"}

    alert = {
        "alert_type": alert_type,
        "severity": severity,
        "provider": provider,
        "title": title,
        "message": message,
        "details": details or {},
        "status": "open",
        "ts": now,
        "ack_at": None,
    }
    await db.api_alerts.insert_one(alert)

    # Email dispatch
    cfg = await db.alert_config.find_one({"_id": "main"}, {"_id": 0}) or {}
    if cfg.get("email_enabled") and cfg.get(f"email_on_{alert_type.lower()}", True):
        html = f"""
        <h2 style="color:{'#dc2626' if severity == 'HIGH' else '#f59e0b'}">{title}</h2>
        <p><strong>Provider:</strong> {provider}</p>
        <p><strong>Severity:</strong> {severity}</p>
        <p>{message}</p>
        <pre style="background:#f3f4f6;padding:12px;border-radius:8px">{(details or {})}</pre>
        <hr/>
        <small>Inviato da GoLevents API Cost Observatory · {now.isoformat()}</small>
        """
        sent = await _send_email_via_resend(f"[GoLevents Alert] {title}", html)
        if not sent:
            await _send_email_via_smtp(f"[GoLevents Alert] {title}", html)

    return {"created": True, "alert": {k: v for k, v in alert.items() if k != "_id"}}


async def check_budget_alerts() -> List[Dict[str, Any]]:
    """Scansiona budget per ogni provider."""
    alerts: List[Dict[str, Any]] = []
    today = datetime.now(timezone.utc)
    month_start = datetime(today.year, today.month, 1, tzinfo=timezone.utc)

    pipe = [
        {"$match": {"ts": {"$gte": month_start}}},
        {"$group": {"_id": "$provider", "total_cost": {"$sum": "$cost_usd"},
                    "calls": {"$sum": 1}}},
    ]
    rows = await db.api_usage_logs.aggregate(pipe).to_list(None)
    spend_by_provider = {r["_id"]: r for r in rows}

    async for budget in db.api_budgets.find({}, {"_id": 1, "monthly_limit_usd": 1, "warning_pct": 1}):
        provider = budget["_id"]
        limit = float(budget.get("monthly_limit_usd") or 0)
        warn_pct = float(budget.get("warning_pct") or DEFAULT_BUDGET_WARNING_PCT)
        if limit <= 0:
            continue
        used = float(spend_by_provider.get(provider, {}).get("total_cost") or 0)
        pct = used / limit * 100

        if pct >= 100:
            res = await _create_alert(
                "BUDGET_EXCEEDED", "HIGH", provider,
                f"Budget {provider} superato",
                f"Hai usato ${used:.2f} su ${limit:.2f} ({pct:.1f}%) del budget mensile.",
                {"used_usd": used, "limit_usd": limit, "pct": pct},
            )
            alerts.append(res)
        elif pct >= warn_pct:
            res = await _create_alert(
                "BUDGET_WARNING", "MEDIUM", provider,
                f"Budget {provider} al {pct:.0f}%",
                f"Hai usato ${used:.2f} su ${limit:.2f}. Restano ${limit - used:.2f}.",
                {"used_usd": used, "limit_usd": limit, "pct": pct},
            )
            alerts.append(res)
    return alerts


async def check_low_balance_alerts() -> List[Dict[str, Any]]:
    """Polling balance reale per provider supportati."""
    alerts: List[Dict[str, Any]] = []
    for provider in PROVIDERS_TO_CHECK:
        try:
            bal = await get_provider_balance(provider)
            real = bal.get("real_polling")
            # DeepL char left
            if real and real.get("char_left") is not None:
                if real["char_left"] < LOW_BALANCE_THRESHOLDS["deepl_char_left"]:
                    res = await _create_alert(
                        "LOW_BALANCE", "MEDIUM", provider,
                        f"Crediti {provider} bassi",
                        f"Restano {real['char_left']} caratteri su {real['char_limit']}",
                        {"char_left": real["char_left"], "char_limit": real["char_limit"]},
                    )
                    alerts.append(res)
            # Estimated remaining
            rem = bal.get("remaining_usd")
            if rem is not None and rem < LOW_BALANCE_THRESHOLDS["remaining_usd"]:
                res = await _create_alert(
                    "LOW_BALANCE", "MEDIUM", provider,
                    f"Budget {provider} quasi esaurito",
                    f"Restano stimati ${rem:.2f} sul budget mensile",
                    {"remaining_usd": rem},
                )
                alerts.append(res)
        except Exception as e:
            logger.warning(f"check_low_balance {provider}: {e}")
    return alerts


async def check_api_health_alerts() -> List[Dict[str, Any]]:
    """API_DOWN + API_INTERMITTENT detection."""
    alerts: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    win_30m = now - timedelta(minutes=API_DOWN_WINDOW_MIN)
    win_24h = now - timedelta(hours=24)

    pipe_30m = [
        {"$match": {"ts": {"$gte": win_30m}}},
        {"$sort": {"ts": -1}},
        {"$group": {
            "_id": "$provider",
            "total": {"$sum": 1},
            "fails": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
            "last_error_code": {"$first": "$error_code"},
            "last_error_msg": {"$first": "$error_msg"},
            "last_error_ts": {"$first": "$ts"},
        }},
    ]
    rows30 = await db.api_usage_logs.aggregate(pipe_30m).to_list(None)
    for r in rows30:
        provider = r["_id"]
        if r["total"] >= API_DOWN_FAIL_COUNT and r["fails"] >= API_DOWN_FAIL_COUNT:
            # Tutti gli ultimi N falliti?
            recent = await db.api_usage_logs.find(
                {"provider": provider, "ts": {"$gte": win_30m}},
                {"_id": 0, "status": 1}
            ).sort("ts", -1).limit(API_DOWN_FAIL_COUNT).to_list(API_DOWN_FAIL_COUNT)
            if all(x["status"] == "failed" for x in recent) and len(recent) >= API_DOWN_FAIL_COUNT:
                res = await _create_alert(
                    "API_DOWN", "HIGH", provider,
                    f"API {provider} non funzionante",
                    f"{API_DOWN_FAIL_COUNT}+ chiamate consecutive fallite. Motivo: {r['last_error_code'] or 'UNKNOWN'}",
                    {"last_error_code": r["last_error_code"],
                     "last_error_msg": r["last_error_msg"],
                     "fails_in_window_min": API_DOWN_WINDOW_MIN, "fails": r["fails"]},
                )
                alerts.append(res)

    pipe_24h = [
        {"$match": {"ts": {"$gte": win_24h}}},
        {"$group": {
            "_id": "$provider",
            "total": {"$sum": 1},
            "fails": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}},
        }},
    ]
    rows24 = await db.api_usage_logs.aggregate(pipe_24h).to_list(None)
    for r in rows24:
        if r["total"] < 10:
            continue
        provider = r["_id"]
        rate = r["fails"] / r["total"] * 100
        if rate >= INTERMITTENT_THRESHOLD_PCT:
            res = await _create_alert(
                "API_INTERMITTENT", "MEDIUM", provider,
                f"API {provider} instabile",
                f"Failure rate {rate:.1f}% nelle ultime 24h ({r['fails']}/{r['total']} chiamate)",
                {"fail_rate_pct": rate, "fails": r["fails"], "total": r["total"]},
            )
            alerts.append(res)
    return alerts


async def run_all_alert_checks() -> Dict[str, Any]:
    """Cron entrypoint."""
    out: Dict[str, Any] = {"ts": datetime.now(timezone.utc).isoformat()}
    out["budget"] = await check_budget_alerts()
    out["low_balance"] = await check_low_balance_alerts()
    out["api_health"] = await check_api_health_alerts()
    new_alerts = sum(1 for v in out.values() if isinstance(v, list)
                     for x in v if isinstance(x, dict) and x.get("created"))
    out["new_alerts_count"] = new_alerts
    return out


async def list_open_alerts(limit: int = 50) -> List[Dict[str, Any]]:
    cursor = db.api_alerts.find({"status": "open"}, {"_id": 0}).sort("ts", -1).limit(limit)
    return await cursor.to_list(limit)


async def acknowledge_alert(alert_id: str) -> bool:
    from bson import ObjectId
    try:
        result = await db.api_alerts.update_one(
            {"_id": ObjectId(alert_id)},
            {"$set": {"status": "acknowledged", "ack_at": datetime.now(timezone.utc)}},
        )
        return result.modified_count > 0
    except Exception:
        return False


async def acknowledge_all_for_provider(provider: str) -> int:
    result = await db.api_alerts.update_many(
        {"provider": provider, "status": "open"},
        {"$set": {"status": "acknowledged", "ack_at": datetime.now(timezone.utc)}},
    )
    return result.modified_count
