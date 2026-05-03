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
    """Esegue il sync programmato. Prova prima API-Football, poi matchesio come fallback."""
    try:
        if await _has_football_api_configured():
            logger.info("Scheduler: avvio sync via API-Football (provider primario)")
            try:
                from services.football_api_sync import sync_via_api_football
                stats = await sync_via_api_football()
                if stats.get("success"):
                    logger.info(
                        f"Scheduler API-Football OK. Inseriti={stats.get('total_inserted')}, "
                        f"aggiornati={stats.get('total_updated')}, "
                        f"leghe sincronizzate={stats.get('leagues_synced')}, "
                        f"loghi aggiunti={stats.get('logos_added')}"
                    )
                    return
                logger.warning(f"API-Football fallita: {stats.get('error')}. Fallback a matchesio.")
            except Exception as e:
                logger.exception(f"Errore API-Football, fallback matchesio: {e}")
        else:
            logger.info("Scheduler: API-Football non configurata, uso matchesio.com")

        # Fallback automatico: matchesio
        stats = await sync_all_competitions(replace_all=False)
        logger.info(
            f"Scheduler matchesio OK. Inseriti={stats['total_inserted']}, "
            f"aggiornati={stats['total_updated']}, in DB={stats.get('total_in_db', 0)}"
        )
    except Exception as e:
        logger.exception(f"Scheduler: errore durante sync: {e}")


def start_scheduler():
    """
    Avvia lo scheduler con sync 2 volte al giorno:
    - 04:00 UTC (06:00 Italia) - aggiornamento mattina
    - 19:00 UTC (21:00 Italia) - cattura annunci serali UEFA/Lega
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
    _scheduler.start()
    logger.info("AsyncIOScheduler avviato (sync alle 04:00 e 19:00 UTC = 06:00 e 21:00 Italia)")


def stop_scheduler():
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("AsyncIOScheduler fermato")
