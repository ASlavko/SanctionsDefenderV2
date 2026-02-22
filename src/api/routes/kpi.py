from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.db.models import SanctionRecord, ImportLog
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy import func

router = APIRouter()

class SanctionListBreakdown(BaseModel):
    individual_count: int = 0
    entity_count: int = 0
    aircraft_count: int = 0
    vessel_count: int = 0
    other_count: int = 0

class SanctionListKPI(BaseModel):
    source: str
    last_update: Optional[datetime] = None
    records_added: int = 0
    records_updated: int = 0
    records_removed: int = 0
    total_records: int = 0
    breakdown: SanctionListBreakdown

@router.get("/sanction-lists", response_model=List[SanctionListKPI])
def get_sanction_lists_kpi(days: int = 1, db: Session = Depends(get_db)):
    """
    Returns KPI metrics for each active Sanction List (EU, UK, US).
    Supports aggregating stats over the last N days.
    """
    from datetime import timedelta
    
    # Calculate timestamp threshold
    threshold = datetime.utcnow() - timedelta(days=days)

    # 1. Identify distinct list types from SanctionRecord
    list_types = db.query(SanctionRecord.list_type).distinct().all()
    list_types = [t[0] for t in list_types if t[0]]
    
    standard_lists = ["EU", "UK", "US"]
    for l in standard_lists:
        if l not in list_types:
            list_types.append(l)
    
    list_types = list(set(list_types))
    
    results = []
    
    for list_type in list_types:
        # A. Get latest import log for last_update status
        latest_import = db.query(ImportLog).filter(ImportLog.source == list_type).order_by(ImportLog.timestamp.desc()).first()
        last_update = latest_import.timestamp if latest_import else None
        
        # Aggregate counts over the time window
        period_stats = db.query(
            func.sum(ImportLog.records_added),
            func.sum(ImportLog.records_updated),
            func.sum(ImportLog.records_removed)
        ).filter(
            ImportLog.source == list_type,
            ImportLog.timestamp >= threshold,
            ImportLog.status == "SUCCESS"
        ).first()

        added = int(period_stats[0] or 0)
        updated = int(period_stats[1] or 0)
        removed = int(period_stats[2] or 0)
        
        # B. Get Total Records count
        total_count = db.query(SanctionRecord).filter(
            SanctionRecord.list_type == list_type
        ).count()
        
        # C. Get Breakdown
        breakdown_query = db.query(
            SanctionRecord.entity_type, 
            func.count(SanctionRecord.id)
        ).filter(
            SanctionRecord.list_type == list_type
        ).group_by(SanctionRecord.entity_type).all()
        
        bd_map = {"individual": 0, "entity": 0, "aircraft": 0, "vessel": 0, "other": 0}
        
        for etype, count in breakdown_query:
            if not etype:
                bd_map["other"] += count
                continue
            
            etype_lower = etype.lower()
            if "individual" in etype_lower or "person" in etype_lower:
                bd_map["individual"] += count
            elif "entity" in etype_lower or "enterprise" in etype_lower or "company" in etype_lower:
                bd_map["entity"] += count
            elif "aircraft" in etype_lower:
                bd_map["aircraft"] += count
            elif "vessel" in etype_lower or "ship" in etype_lower:
                bd_map["vessel"] += count
            else:
                bd_map["other"] += count
                
        kpi = SanctionListKPI(
            source=list_type,
            last_update=last_update,
            records_added=added,
            records_updated=updated,
            records_removed=removed,
            total_records=total_count,
            breakdown=SanctionListBreakdown(
                individual_count=bd_map["individual"],
                entity_count=bd_map["entity"],
                aircraft_count=bd_map["aircraft"],
                vessel_count=bd_map["vessel"],
                other_count=bd_map["other"]
            )
        )
        results.append(kpi)
        
    return results
