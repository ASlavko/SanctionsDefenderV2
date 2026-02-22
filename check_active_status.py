from src.db.session import SessionLocal
from src.db.models import SanctionRecord
from sqlalchemy import func

db = SessionLocal()

# Check active status distribution
print("=== Active Status by List Type ===")
status_dist = db.query(
    SanctionRecord.list_type,
    SanctionRecord.is_active,
    func.count(SanctionRecord.id)
).group_by(SanctionRecord.list_type, SanctionRecord.is_active).all()

for lt, active, count in status_dist:
    print(f"{lt} - Active={active}: {count}")

# Total counts without active filter
print("\n=== Total Counts (All Records) ===")
all_counts = db.query(
    SanctionRecord.list_type,
    func.count(SanctionRecord.id)
).group_by(SanctionRecord.list_type).all()

for lt, count in all_counts:
    print(f"{lt}: {count}")

db.close()
