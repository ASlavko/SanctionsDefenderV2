
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.api.services.engine import search_engine
from src.api.services.search_logs import create_search_log
from src.api.search_log_schemas import SearchLogCreate, SearchLogRead
from typing import Any
from pydantic import BaseModel

router = APIRouter(prefix="/single_screening", tags=["SingleScreening"])

class SingleScreeningRequest(BaseModel):
    search_term: str
    search_type: str = "COMPANY"
    threshold: int = 85
    user_id: str | None = None
    company_id: str | None = None

@router.post("/")
def single_screening(
    req: SingleScreeningRequest,
    db: Session = Depends(get_db),
):
    # 1. Run search
    matches = search_engine.search(req.search_term, threshold=req.threshold)
    result_count = len(matches)
    # Convert matches to dicts for JSON serialization
    def to_dict_safe(obj):
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        return obj
    matches_serializable = [to_dict_safe(m) for m in matches]
    # 2. Log search
    log = SearchLogCreate(
        search_term=req.search_term,
        search_type=req.search_type,
        result_count=result_count,
        user_id=str(req.user_id) if req.user_id else "unknown",
        company_id=str(req.company_id) if req.company_id else "unknown",
    )
    create_search_log(db, log)
    # 3. Return results
    return {"matches": matches_serializable, "result_count": result_count}
