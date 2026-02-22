from src.db.session import SessionLocal
from src.db.models import SanctionRecord, ImportLog
from sqlalchemy import func

db = SessionLocal()

# Check EU records
print("=== EU Sanction Records ===")
eu_count = db.query(SanctionRecord).filter(
    SanctionRecord.list_type == "EU",
    SanctionRecord.is_active == True
).count()
print(f"Active EU records: {eu_count}")

# Check all list types
print("\n=== All List Types ===")
list_types = db.query(SanctionRecord.list_type, func.count(SanctionRecord.id)).filter(
    SanctionRecord.is_active == True
).group_by(SanctionRecord.list_type).all()
for lt, count in list_types:
    print(f"{lt}: {count}")

# Check import logs
print("\n=== Import Logs ===")
logs = db.query(ImportLog).order_by(ImportLog.timestamp.desc()).limit(10).all()
for log in logs:
    print(f"{log.source}: {log.timestamp} - Added: {log.records_added}, Updated: {log.records_updated}, Removed: {log.records_removed}")

# Check a few EU records
print("\n=== Sample EU Records ===")
eu_samples = db.query(SanctionRecord).filter(SanctionRecord.list_type == "EU").limit(5).all()
for rec in eu_samples:
    print(f"ID: {rec.id}, Name: {rec.original_name}, Active: {rec.is_active}")

db.close()
