"""
Scheduler APScheduler per sync automatico da matchesio.com ogni 6 ore.
"""
import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from services.matchesio_sync import sync_all_competitions

logger = logging.getLogger(__name__)
_scheduler: AsyncIOScheduler | None = None


async def _run_sync_job():
    try:
        # Cron: usa upsert (replace_all=False) per sicurezza:
        # - non cancella eventi custom dell'admin
        # - aggiorna solo gli esistenti
        logger.info("Scheduler: avvio sync programmato matchesio.com (upsert)")
        stats = await sync_all_competitions(replace_all=False)
        logger.info(
            f"Scheduler: sync completato. Inseriti={stats['total_inserted']}, "
            f"aggiornati={stats['total_updated']}, in DB={stats.get('total_in_db', 0)}, "
            f"errori={len(stats.get('errors', []))}"
        )
    except Exception as e:
        logger.exception(f"Scheduler: errore durante sync: {e}")


def start_scheduler():
    """Avvia lo scheduler. Sync ogni 6 ore (00:00, 06:00, 12:00, 18:00 UTC)."""
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = AsyncIOScheduler(timezone="UTC")
    # Cron 4 volte al giorno
    _scheduler.add_job(
        _run_sync_job,
        CronTrigger(hour="0,6,12,18", minute=0),
        id="matchesio_sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    logger.info("AsyncIOScheduler avviato (cron: 0,6,12,18 UTC)")


def stop_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("AsyncIOScheduler fermato")
