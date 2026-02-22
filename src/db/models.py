from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from src.db.session import Base
import enum
from datetime import datetime

class MatchStatus(str, enum.Enum):
    PENDING = "PENDING"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    TRUE_MATCH = "TRUE_MATCH"
    NO_MATCH = "NO_MATCH"

class SanctionRecord(Base):
    __tablename__ = "sanctions"

    id = Column(String, primary_key=True, index=True) # Unique ID (e.g., "EU-123")
    list_type = Column(String, index=True) # EU, UK, US
    original_name = Column(String)
    normalized_name = Column(String, index=True)
    alias_names = Column(Text) # JSON or pipe-separated
    
    program = Column(String)
    nationality = Column(String)
    birth_date = Column(String)
    
    # New fields
    entity_type = Column(String) # Individual, Entity, Vessel, Aircraft
    gender = Column(String) # Male, Female, etc.
    url = Column(String) # Source URL for more info
    
    # Additional fields from comparison
    un_id = Column(String) # United Nation ID
    remark = Column(Text) # Remarks/Notes
    function = Column(String) # Job Title/Function

    is_active = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # For tracking changes
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)

class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String) # EU, UK, US, US_NON_SDN
    records_added = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_removed = Column(Integer, default=0)
    status = Column(String) # SUCCESS, FAILED, IN_PROGRESS
    error_message = Column(Text, nullable=True)

class ChangeLog(Base):
    __tablename__ = "change_logs"

    id = Column(Integer, primary_key=True, index=True)
    import_log_id = Column(Integer, ForeignKey("import_logs.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    record_id = Column(String, index=True)
    change_type = Column(String) # ADDED, UPDATED, REMOVED
    field_changed = Column(String, nullable=True) # e.g., "original_name"
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    import_log = relationship("ImportLog")

class MatchDecision(Base):
    __tablename__ = "match_decisions"

    id = Column(Integer, primary_key=True, index=True)
    search_term_normalized = Column(String, index=True)
    sanction_id = Column(String, ForeignKey("sanctions.id"))
    decision = Column(Enum(MatchStatus))
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String) # If we have auth
    revoked = Column(Boolean, default=False)


class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    search_term = Column(String, nullable=False)
    search_type = Column(String, nullable=False)  # 'COMPANY' or 'INDIVIDUAL'
    result_count = Column(Integer, nullable=False)
    user_id = Column(String, nullable=True)
    company_id = Column(String, nullable=True)

# Audit log for all decision actions
class DecisionAudit(Base):
    __tablename__ = "decision_audit"

    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(Integer, ForeignKey("match_decisions.id"))
    action = Column(String)  # create, update, revoke
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    user_id = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    comment = Column(String, nullable=True)

class ScreeningBatch(Base):
    __tablename__ = "screening_batches"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    total_records = Column(Integer)
    flagged_count = Column(Integer)
    status = Column(String) # PROCESSING, COMPLETED, FAILED

class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("screening_batches.id"))
    input_name = Column(String)
    match_status = Column(Enum(MatchStatus), default=MatchStatus.PENDING)
    
    # Relationship to matches
    matches = relationship("ScreeningMatch", back_populates="result", cascade="all, delete-orphan")
    batch = relationship("ScreeningBatch")

class ScreeningMatch(Base):
    __tablename__ = "screening_matches"

    id = Column(Integer, primary_key=True, index=True)
    screening_result_id = Column(Integer, ForeignKey("screening_results.id"))
    sanction_id = Column(String, ForeignKey("sanctions.id"))
    match_score = Column(Float)
    match_name = Column(String) # The specific name/alias that matched
    
    result = relationship("ScreeningResult", back_populates="matches")
    sanction = relationship("SanctionRecord")
    sanction = relationship("SanctionRecord")
