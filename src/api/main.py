from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.db.session import engine, Base, SessionLocal
from src.api.services.engine import search_engine
from src.api.routes import batch
from src.api.routes import system
from src.api.routes import audit
from src.api.routes import decision
from src.api.routes import search_log
from src.api.routes import single_screening
from src.api.routes import kpi
from src.services.updater import run_daily_update
import logging

logger = logging.getLogger(__name__)

# Create tables on startup (for dev/prototype speed)
Base.metadata.create_all(bind=engine)

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load data into memory
    db = SessionLocal()
    try:
        search_engine.load_data(db)
    finally:
        db.close()
    
    # Start Scheduler
    # Run daily at 03:00 AM system time
    scheduler.add_job(
        run_daily_update,
        trigger=CronTrigger(hour=3, minute=0),
        id="daily_sanctions_update",
        name="Update Sanctions from Official Sources",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduler started. Daily update scheduled for 03:00 AM.")

    yield
    
    # Shutdown logic
    scheduler.shutdown()

app = FastAPI(title="SanctionDefenderV2", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Only allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(batch.router, prefix="/api/v1/batch", tags=["Batch Screening"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])
app.include_router(audit.router, prefix="/api/v1", tags=["Audit"])
app.include_router(decision.router, prefix="/api/v1", tags=["Decision"])
app.include_router(search_log.router, prefix="/api/v1", tags=["SearchLog"])
app.include_router(single_screening.router, prefix="/api/v1", tags=["SingleScreening"])
app.include_router(kpi.router, prefix="/api/v1/kpi", tags=["KPI"])

@app.post("/api/v1/admin/trigger-update")
async def trigger_update(background_tasks: BackgroundTasks):
    """Manually trigger the update process in the background."""
    background_tasks.add_task(run_daily_update)
    return {"status": "Update triggered in background"}

@app.get("/")
def health_check():
    return {"status": "ok", "engine_loaded": search_engine.initialized}

@app.get("/api/v1/system/status")
def system_status_direct():
    """Directly expose system status to avoid router import issues."""
    import subprocess
    engine = search_engine.status()
    try:
        branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        branch = None
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        commit = None
    return {
        "status": "ok",
        "engine": engine,
        "git": {"branch": branch, "commit": commit}
    }
