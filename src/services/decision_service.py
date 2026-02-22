from src.db.session import SessionLocal
from src.db.models import MatchDecision, DecisionAudit, MatchStatus
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional

# Utility function to create, update, or revoke a decision and log audit

def set_match_decision(
    search_term_normalized: str,
    sanction_id: str,
    decision: MatchStatus,
    user_id: str,
    comment: Optional[str] = None,
    db: Optional[Session] = None
):
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True
    try:
        # Revoke any previous active decision for this pair
        prev = db.query(MatchDecision).filter_by(
            search_term_normalized=search_term_normalized,
            sanction_id=sanction_id,
            revoked=False
        ).first()
        if prev:
            prev.revoked = True
            db.add(prev)
            db.flush()
            db.add(DecisionAudit(
                decision_id=prev.id,
                action="revoke",
                old_value=prev.decision.value,
                new_value=None,
                user_id=user_id,
                timestamp=datetime.utcnow(),
                comment="Auto-revoked by new decision"
            ))
        # Create new decision
        new_decision = MatchDecision(
            search_term_normalized=search_term_normalized,
            sanction_id=sanction_id,
            decision=decision,
            comment=comment,
            created_at=datetime.utcnow(),
            user_id=user_id,
            revoked=False
        )
        db.add(new_decision)
        db.flush()
        db.add(DecisionAudit(
            decision_id=new_decision.id,
            action="create",
            old_value=None,
            new_value=decision.value,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            comment=comment
        ))
        db.commit()
        return new_decision
    except Exception as e:
        db.rollback()
        raise
    finally:
        if own_session:
            db.close()

# Example usage:
# set_match_decision("ivan_novak", "EU-123", MatchStatus.FALSE_POSITIVE, "user1", "Not a match")
