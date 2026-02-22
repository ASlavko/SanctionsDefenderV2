from src.db.session import SessionLocal
from src.db.models import SanctionRecord

db = SessionLocal()

# Count inactive EU records before
inactive_count = db.query(SanctionRecord).filter(
    SanctionRecord.list_type == "EU",
    SanctionRecord.is_active == False
).count()

print(f"Inactive EU records before: {inactive_count}")

# Reactivate all EU records
result = db.query(SanctionRecord).filter(
    SanctionRecord.list_type == "EU",
    SanctionRecord.is_active == False
).update(
    {SanctionRecord.is_active: True},
    synchronize_session=False
)

db.commit()

print(f"Reactivated {result} EU records")

# Verify
active_count = db.query(SanctionRecord).filter(
    SanctionRecord.list_type == "EU",
    SanctionRecord.is_active == True
).count()

print(f"Active EU records after: {active_count}")

db.close()
