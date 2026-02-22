from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class SearchLogBase(BaseModel):
    search_term: str
    search_type: str  # 'COMPANY' or 'INDIVIDUAL'
    result_count: int
    user_id: Optional[str] = None
    company_id: Optional[str] = None

class SearchLogCreate(SearchLogBase):
    pass

class SearchLogRead(SearchLogBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True
