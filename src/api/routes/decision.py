from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.db.models import MatchDecision, DecisionAudit, MatchStatus
from src.services.decision_service import set_match_decision
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()

class DecisionCreateRequest(BaseModel):
    search_term_normalized: str
    sanction_id: str
    decision: MatchStatus
    user_id: str
    comment: Optional[str] = None

@router.post("/decision/create")
def create_decision(req: DecisionCreateRequest, db: Session = Depends(get_db)):
    new_decision = set_match_decision(
        search_term_normalized=req.search_term_normalized,
        sanction_id=req.sanction_id,
        decision=req.decision,
        user_id=req.user_id,
        comment=req.comment,
        db=db
    )
    return {"id": new_decision.id, "status": "created"}

@router.get("/decision/list")
def list_decisions(active_only: bool = True, db: Session = Depends(get_db)):
    q = db.query(MatchDecision)
    if active_only:
        q = q.filter_by(revoked=False)
    return [
        {
            "id": d.id,
            "search_term_normalized": d.search_term_normalized,
            "sanction_id": d.sanction_id,
            "decision": d.decision,
            "comment": d.comment,
            "created_at": d.created_at,
            "user_id": d.user_id,
            "revoked": d.revoked
        }
        for d in q.all()
    ]

@router.get("/decision/audit/{decision_id}")
def audit_history(decision_id: int, db: Session = Depends(get_db)):
    audits = db.query(DecisionAudit).filter_by(decision_id=decision_id).order_by(DecisionAudit.timestamp).all()
    return [
        {
            "id": a.id,
            "action": a.action,
            "old_value": a.old_value,
            "new_value": a.new_value,
            "user_id": a.user_id,
            "timestamp": a.timestamp,
            "comment": a.comment
        }
        for a in audits
    ]
