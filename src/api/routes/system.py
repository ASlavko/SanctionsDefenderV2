from fastapi import APIRouter
from src.api.services.engine import search_engine
import subprocess

router = APIRouter()

@router.get("/status")
def system_status():
    # Engine details
    engine = search_engine.status()

    # Git details (best-effort; safe fallbacks)
    branch = None
    commit = None
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
        "git": {
            "branch": branch,
            "commit": commit
        }
    }
