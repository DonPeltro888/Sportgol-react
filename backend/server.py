from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from database import db, client
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List
import uuid
from datetime import datetime, timezone

# Import route modules
from routes import events, categories, search
from routes import admin_auth, admin_content, admin_integrations, admin_providers
from routes import upload, seo, sectors, leagues, teams, prerender
from routes import sync as sync_routes
from routes import seo_admin, seo_targets, seo_tools, data_tools_health, data_tools_quality

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Create the main app without a prefix
app = FastAPI(title="Golevents API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Golevents API v1.0", "status": "active"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)


# Health check endpoint per monitoring/uptime
@app.get("/api/health")
async def health_check():
    """Endpoint health check con verifica DB e scheduler."""
    from datetime import datetime, timezone
    health = {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "db": "unknown",
        "scheduler": "unknown",
    }
    try:
        await db.command("ping")
        health["db"] = "ok"
        health["events_count"] = await db.events.count_documents({})
        health["leagues_count"] = await db.leagues.count_documents({})
        health["teams_count"] = await db.teams.count_documents({})
    except Exception as e:
        health["status"] = "degraded"
        health["db"] = f"error: {e}"
    try:
        from services.scheduler import _scheduler
        health["scheduler"] = "running" if _scheduler and _scheduler.running else "stopped"
    except Exception:
        health["scheduler"] = "unknown"
    return health


# Include new feature routes
app.include_router(events.router)
app.include_router(categories.router)
app.include_router(search.router)
app.include_router(admin_auth.router)
app.include_router(admin_content.router)
app.include_router(upload.router)
app.include_router(seo.router)
app.include_router(sectors.router)
app.include_router(leagues.router)
app.include_router(teams.router)
app.include_router(sync_routes.router)
app.include_router(prerender.router)
app.include_router(admin_integrations.router)
app.include_router(admin_providers.router)
app.include_router(seo_admin.router)
app.include_router(seo_targets.router)
app.include_router(seo_tools.router)
app.include_router(data_tools_health.router)
app.include_router(data_tools_quality.router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    import asyncio
    logger.info("Starting Golevents API...")
    logger.info(f"Connected to MongoDB: {os.environ['DB_NAME']}")
    # TTL index per auto-cleanup admin tokens scaduti
    try:
        from database import db
        await db.admin_tokens.create_index("expires_at", expireAfterSeconds=0)
        logger.info("TTL index su admin_tokens.expires_at creato")
    except Exception as e:
        logger.warning(f"TTL index admin_tokens già esistente o errore: {e}")
    # Index su events.slug per lookup veloce
    try:
        from database import db
        await db.events.create_index("slug", unique=False, sparse=True)
        logger.info("Index su events.slug creato")
    except Exception as e:
        logger.warning(f"Index events.slug già esistente o errore: {e}")

    # Background task: backfill slugs + scheduler avvio (non blocca startup K8s health check)
    async def _bg_init():
        try:
            from database import db
            missing = await db.events.count_documents({"slug": {"$exists": False}})
            if missing > 0:
                logger.info(f"Backfilling slugs for {missing} events (background)...")
                from services.event_slug import backfill_all_slugs
                stats = await backfill_all_slugs()
                logger.info(f"Slug backfill done: {stats}")
        except Exception as e:
            logger.error(f"Errore backfill slugs (background): {e}")
        try:
            from services.scheduler import start_scheduler
            start_scheduler()
            logger.info("Scheduler avviato (auto-sync 06:00 + 21:00 Italia)")
        except Exception as e:
            logger.error(f"Errore avvio scheduler: {e}")

    asyncio.create_task(_bg_init())
    logger.info("Startup completato (backfill+scheduler in background)")

@app.on_event("shutdown")
async def shutdown_db_client():
    try:
        from services.scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass
    client.close()
    logger.info("MongoDB connection closed")