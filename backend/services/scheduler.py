"""
Scheduler APScheduler per sync automatico.
Orari: 04:00 UTC (06:00 Italia) + 19:00 UTC (21:00 Italia).
Priorità:
  1. API-Football (se configurata e abilitata in /admin/integrations)
  2. matchesio.com (fallback automatico se API non disponibile)
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from services.matchesio_sync import sync_all_competitions
from database import db

logger = logging.getLogger(__name__)
_scheduler: AsyncIOScheduler | None = None


async def _has_football_api_configured() -> bool:
    """Ritorna True se l'API key è configurata e abilitata."""
    doc = await db.settings.find_one({"_id": "integrations"}, {"_id": 0})
    if not doc:
        return False
    fa = doc.get("football_api", {})
    return bool(fa.get("enabled") and fa.get("api_key"))


async def _run_sync_job():
    """Esegue il MIX 5-fonti programmato (OpenFootball + matchesio + APIfootball + TheSportsDB)."""
    try:
        logger.info("Scheduler: avvio MIX 5-fonti")
        # OpenFootball
        try:
            from services.openfootball_sync import sync_via_openfootball
            s = await sync_via_openfootball()
            logger.info(f"OpenFootball: +{s.get('total_inserted',0)} eventi, {s.get('leagues_synced',0)} leghe")
        except Exception as e:
            logger.error(f"OpenFootball errore: {e}")

        # matchesio
        try:
            stats = await sync_all_competitions(replace_all=False)
            logger.info(f"matchesio: +{stats.get('total_inserted',0)} eventi, leghe vuote={len(stats.get('leagues_empty',[]))}")
        except Exception as e:
            logger.error(f"matchesio errore: {e}")

        # APIfootball.com (se key)
        settings_doc = await db.settings.find_one({"_id": "integrations"}, {"_id": 0}) or {}
        af_cfg = settings_doc.get("apifootball", {})
        if af_cfg.get("enabled") and af_cfg.get("api_key"):
            try:
                from services.apifootball_sync import sync_via_apifootball
                s = await sync_via_apifootball()
                logger.info(f"APIfootball: +{s.get('total_inserted',0)} eventi, {s.get('logos_added',0)} loghi")
            except Exception as e:
                logger.error(f"APIfootball errore: {e}")

        # TheSportsDB
        try:
            from services.thesportsdb_sync import sync_via_thesportsdb
            s = await sync_via_thesportsdb()
            logger.info(f"TheSportsDB: +{s.get('total_inserted',0)} eventi, {s.get('logos_added',0)} loghi")
        except Exception as e:
            logger.error(f"TheSportsDB errore: {e}")

        logger.info("Scheduler: MIX completato")
    except Exception as e:
        logger.exception(f"Scheduler: errore generale: {e}")


async def _run_normalize_backstop():
    """Backstop: normalizza qualsiasi event/team/league con _normalized != True."""
    try:
        from services.db_normalize import backstop_normalize_all
        counters = await backstop_normalize_all(limit=10000)
        logger.info(f"Backstop normalize: {counters}")
    except Exception as e:
        logger.error(f"Backstop normalize error: {e}")


async def _run_health_autofix():
    """Auto-fix scheduler: bulk fix loghi e dati mancanti via Perplexity + Gemini Vision."""
    try:
        from scripts.bulk_fix_logos import get_targets, fix_one_with_sem
        import asyncio as _asyncio
        targets = await get_targets()
        if not targets:
            logger.info("Health autofix: no targets")
            return
        logger.info(f"Health autofix: starting on {len(targets)} teams")
        sem = _asyncio.Semaphore(4)
        tasks = [fix_one_with_sem(sem, t["slug"], t.get("name", ""), i + 1, len(targets)) for i, t in enumerate(targets)]
        results = await _asyncio.gather(*tasks, return_exceptions=True)
        fixed = sum(1 for r in results if isinstance(r, dict) and r.get("applied"))
        logger.info(f"Health autofix DONE: {fixed}/{len(targets)} fixed")
    except Exception as e:
        logger.error(f"Health autofix error: {e}")


async def _run_daily_snapshot():
    """Snapshot giornaliero metriche sync-quality per il trend storico."""
    try:
        from datetime import datetime, timezone, timedelta
        from database import db
        now = datetime.now(timezone.utc)
        since_24h = (now - timedelta(hours=24)).isoformat()
        snap = {
            "ts": now.replace(microsecond=0).isoformat(),
            "date": now.date().isoformat(),
            "events_total": await db.events.count_documents({}),
            "teams_total": await db.teams.count_documents({}),
            "leagues_total": await db.leagues.count_documents({}),
            "normalized_24h_events": await db.events.count_documents({"_normalized_at": {"$gte": since_24h}}),
            "normalized_24h_teams": await db.teams.count_documents({"_normalized_at": {"$gte": since_24h}}),
            "fixes_24h": await db.health_fixes.count_documents({"ts": {"$gte": since_24h}}),
            "logo_proxied": await db.teams.count_documents({"logo_url": {"$regex": "^/api/seo/team-logo/"}}),
            "logo_missing": await db.teams.count_documents({
                "$or": [{"logo_url": {"$exists": False}}, {"logo_url": ""}, {"logo_url": None}]
            }),
            "events_published": await db.events.count_documents({"seo_status": "Published"}),
            "teams_published": await db.teams.count_documents({"seo_status": "Published"}),
        }
        await db.sync_quality_snapshots.update_one(
            {"date": snap["date"]}, {"$set": snap}, upsert=True
        )
        logger.info(f"Daily snapshot saved: {snap['date']}")
    except Exception as e:
        logger.error(f"Daily snapshot error: {e}")


def start_scheduler():
    """
    Avvia lo scheduler con:
    - 04:00 UTC (06:00 Italia) - sync matchesio mattina
    - 19:00 UTC (21:00 Italia) - sync matchesio sera
    - 04:30 UTC dopo sync mattina) - normalize backstop su nuovi insert
    - 03:00 UTC ogni notte) - health autofix loghi/dati mancanti
    """
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = AsyncIOScheduler(timezone="UTC")
    _scheduler.add_job(
        _run_sync_job,
        CronTrigger(hour="4,19", minute=0),
        id="auto_sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.add_job(
        _run_normalize_backstop,
        CronTrigger(hour="4,19", minute=30),
        id="normalize_backstop",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.add_job(
        _run_health_autofix,
        CronTrigger(hour=3, minute=0),
        id="health_autofix",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.add_job(
        _run_daily_snapshot,
        CronTrigger(hour=2, minute=0),
        id="daily_snapshot",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    logger.info("AsyncIOScheduler avviato: sync 04:00/19:00, normalize-backstop 04:30/19:30, snapshot 02:00, health-autofix 03:00 (UTC)")


def stop_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("AsyncIOScheduler fermato")
