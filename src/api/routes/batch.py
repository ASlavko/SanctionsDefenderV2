from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from src.db.session import get_db, SessionLocal
from src.db.models import ScreeningBatch, ScreeningResult, MatchStatus
from src.api.services.engine import search_engine
import pandas as pd
import io
from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class BatchResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime
    total_records: int
    flagged_count: Optional[int] = None
    status: str

    class Config:
        from_attributes = True

class ScreeningResultResponse(BaseModel):
    id: int
    input_name: str
    match_status: str
    match_score: float
    matched_sanction_id: Optional[str] = None

    class Config:
        from_attributes = True

class BatchDetailResponse(BaseModel):
    batch: BatchResponse
    results: List[ScreeningResultResponse]

def read_csv_robust(content: bytes) -> pd.DataFrame:
    """
    Attempts to read CSV with multiple encodings and separators.
    """
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1", "iso-8859-2"]
    separators = [",", ";", "\t"]
    
    last_error = None
    candidate_df = None
    
    for encoding in encodings:
        for sep in separators:
            try:
                # Try reading
                df = pd.read_csv(io.BytesIO(content), encoding=encoding, sep=sep)
                
                # Heuristic: If we have only 1 column, it might be the wrong separator
                # unless the file genuinely has 1 column.
                # But if we have >1 columns, it is a strong signal we found the right one.
                if len(df.columns) > 1:
                    return df
                
                # If 1 column, keep it as a candidate but keep trying other separators
                candidate_df = df
                
            except Exception as e:
                last_error = e
                continue
    
    # If we found a candidate (even with 1 column), return it
    if candidate_df is not None:
        return candidate_df
        
    raise last_error or Exception("Could not read CSV file")

def process_batch_task(batch_id: int, file_content: bytes, filename: str):
    """
    Background task to process the file and save results.
    Creates its own DB session to avoid using a closed request session.
    """
    db = SessionLocal()
    try:
        logger.info(f"Starting background processing for batch {batch_id}")
        
        # 1. Read File
        if filename.endswith(".csv"):
            df = read_csv_robust(file_content)
        else:
            df = pd.read_excel(io.BytesIO(file_content))
        
        # Assume the column with names is the first one or named Name/name
        # Normalize column names to lower case for search
        cols_lower = [str(c).lower() for c in df.columns]
        
        name_col_idx = 0
        if "name" in cols_lower:
            name_col_idx = cols_lower.index("name")
        elif "naziv" in cols_lower: # Slovenian/Croatian for Name
            name_col_idx = cols_lower.index("naziv")
        elif "ime" in cols_lower:   # Slovenian/Croatian for Name
            name_col_idx = cols_lower.index("ime")
            
        name_col = df.columns[name_col_idx]
        names = df[name_col].astype(str).tolist()

        # 2. Run Search
        results = search_engine.batch_search(names)

        # 3. Save Results
        # Re-query batch to attach to session
        batch = db.query(ScreeningBatch).filter(ScreeningBatch.id == batch_id).first()
        if not batch:
            logger.error(f"Batch {batch_id} not found in background task")
            return

        flagged_count = 0
        
        for res in results:
            status = res["match_status"]
            if status != MatchStatus.NO_MATCH:
                flagged_count += 1
            
            db_result = ScreeningResult(
                batch_id=batch.id,
                input_name=res["input_name"],
                match_status=status,
                match_score=res["max_score"],
                matched_sanction_id=res["potential_match"].id if res["potential_match"] else None
            )
            db.add(db_result)
        
        batch.status = "COMPLETED"
        batch.flagged_count = flagged_count
        db.commit()
        logger.info(f"Batch {batch_id} completed. Flagged: {flagged_count}")
        
    except Exception as e:
        logger.error(f"Error processing batch {batch_id}: {e}")
        # Re-query to avoid detached instance issues
        try:
            batch = db.query(ScreeningBatch).filter(ScreeningBatch.id == batch_id).first()
            if batch:
                batch.status = "FAILED"
                db.commit()
        except Exception as db_e:
            logger.error(f"Failed to update batch status to FAILED: {db_e}")
    finally:
        db.close()

@router.post("/upload", response_model=BatchResponse)
async def upload_batch(
    file: UploadFile = File(...), 
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    if not file.filename.endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload Excel or CSV.")

    content = await file.read()
    
    # Create Batch Record
    batch = ScreeningBatch(
        filename=file.filename,
        total_records=0,
        status="PROCESSING"
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    # Get count
    try:
        if file.filename.endswith(".csv"):
            df = read_csv_robust(content)
        else:
            df = pd.read_excel(io.BytesIO(content))
        batch.total_records = len(df)
        db.commit()
        db.refresh(batch) # Refresh to ensure all fields are up to date for response
    except Exception as e:
        print(f"Error reading file for count: {e}")
        batch.status = "FAILED"
        db.commit()
        raise HTTPException(status_code=400, detail=f"Could not read file content: {str(e)}")

    # Start Background Processing
    # Pass only necessary data, NOT the db session
    background_tasks.add_task(process_batch_task, batch.id, content, file.filename)

    return batch

@router.get("/", response_model=List[BatchResponse])
def list_batches(db: Session = Depends(get_db)):
    return db.query(ScreeningBatch).order_by(ScreeningBatch.uploaded_at.desc()).all()

@router.get("/{batch_id}", response_model=BatchDetailResponse)
def get_batch_results(batch_id: int, db: Session = Depends(get_db)):
    batch = db.query(ScreeningBatch).filter(ScreeningBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    results = db.query(ScreeningResult).filter(ScreeningResult.batch_id == batch_id).all()
    
    return {
        "batch": batch,
        "results": results
    }
