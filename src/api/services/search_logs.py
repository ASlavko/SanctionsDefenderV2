from sqlalchemy.orm import Session
from src.db.models import SearchLog
from src.api.search_log_schemas import SearchLogCreate
from typing import List

def create_search_log(db: Session, log: SearchLogCreate) -> SearchLog:
    db_log = SearchLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_search_logs_by_company(db: Session, company_id: str, user_id: str = None, skip: int = 0, limit: int = 50) -> List[SearchLog]:
    q = db.query(SearchLog).filter(SearchLog.company_id == company_id)
    if user_id:
        q = q.filter(SearchLog.user_id == user_id)
    return q.order_by(SearchLog.timestamp.desc()).offset(skip).limit(limit).all()
