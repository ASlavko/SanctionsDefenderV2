from src.db.session import SessionLocal
from src.db.models import ImportLog, ChangeLog
from sqlalchemy import desc

db = SessionLocal()

# Get all import logs
print("=== Import Logs (Most Recent First) ===")
logs = db.query(ImportLog).order_by(desc(ImportLog.timestamp)).all()
for log in logs:
    print(f"\nID: {log.id}")
    print(f"Source: {log.source}")
    print(f"Timestamp: {log.timestamp}")
    print(f"Status: {log.status}")
    print(f"Added: {log.records_added}, Updated: {log.records_updated}, Removed: {log.records_removed}")
    if log.error_message:
        print(f"Error: {log.error_message}")

# Get change logs for EU
print("\n\n=== EU Change Logs ===")
eu_import_ids = [log.id for log in logs if log.source == "EU"]
if eu_import_ids:
    changes = db.query(ChangeLog).filter(
        ChangeLog.import_log_id.in_(eu_import_ids)
    ).order_by(desc(ChangeLog.timestamp)).limit(20).all()
    
    for change in changes:
        print(f"\nRecord ID: {change.record_id}")
        print(f"Change Type: {change.change_type}")
        print(f"Field: {change.field_changed}")
        print(f"Old: {change.old_value}")
        print(f"New: {change.new_value}")

db.close()
