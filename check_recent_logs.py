from src.db.session import SessionLocal
from src.db.models import ImportLog
from sqlalchemy import desc

db = SessionLocal()

# Get the most recent import logs
print("=== Most Recent Import Logs ===")
logs = db.query(ImportLog).order_by(desc(ImportLog.timestamp)).limit(10).all()
for log in logs:
    print(f"\nID: {log.id}, Source: {log.source}")
    print(f"Timestamp: {log.timestamp}")
    print(f"Status: {log.status}")
    print(f"Added: {log.records_added}, Updated: {log.records_updated}, Removed: {log.records_removed}")
    if log.error_message:
        print(f"Error: {log.error_message}")

db.close()
