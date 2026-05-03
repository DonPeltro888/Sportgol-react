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
    """Esegue il sync programmato. STRATEGIA MIX:
    1. matchesio.com (gratis, veloce) per le ~20 competizioni che supporta
    2. Se API esterna configurata, riempie SOLO le leghe vuote dopo matchesio.
    """
    try:
        # STEP 1: matchesio sempre primo (no costi)
        logger.info("Scheduler: STEP 1 - sync matchesio.com")
        m_stats = await sync_all_competitions(replace_all=False)
        logger.info(f"matchesio: inseriti={m_stats['total_inserted']}, aggiornati={m_stats['total_updated']}, leghe vuote={len(m_stats.get('leagues_empty', []))}")

        # STEP 2: riempi mancanti via API esterna se configurata
        doc = await db.settings.find_one({"_id": "integrations"}, {"_id": 0})
        fa = (doc or {}).get("football_api", {})
        if fa.get("enabled") and fa.get("api_key"):
            provider = fa.get("provider", "api_football")
            empty = [item["league"] for item in m_stats.get("leagues_empty", [])]
            if empty:
                logger.info(f"Scheduler: STEP 2 - {provider} riempie {len(empty)} leghe vuote: {empty}")
                if provider == "football_data":
                    from services.football_data_sync import sync_via_football_data
                    api_stats = await sync_via_football_data(only_empty_leagues=empty)
                else:
                    from services.football_api_sync import sync_via_api_football
                    api_stats = await sync_via_api_football()
                if api_stats.get("success"):
                    logger.info(f"{provider}: riempiti {api_stats.get('total_inserted', 0)} eventi nuovi, {api_stats.get('logos_added', 0)} loghi")
                else:
                    logger.warning(f"{provider} fallito: {api_stats.get('error')}")
            else:
                logger.info("Scheduler: nessuna lega vuota, no chiamate API esterne")
        else:
            logger.info("Scheduler: nessuna API esterna configurata, solo matchesio")
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
