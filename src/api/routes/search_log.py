from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.api.search_log_schemas import SearchLogCreate, SearchLogRead
from src.api.services.search_logs import create_search_log, get_search_logs_by_company
from typing import List

router = APIRouter(prefix="/search_log", tags=["search_log"])

@router.post("/", response_model=SearchLogRead)
def log_search(log: SearchLogCreate, db: Session = Depends(get_db)):
    return create_search_log(db, log)

@router.get("/", response_model=List[SearchLogRead])
def list_search_logs(company_id: str, user_id: str = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return get_search_logs_by_company(db, company_id, user_id, skip, limit)
