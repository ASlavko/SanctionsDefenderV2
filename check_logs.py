from src.db.session import SessionLocal
from src.db.models import ImportLog, ChangeLog
import pandas as pd

def check_logs():
    db = SessionLocal()
    try:
        print("--- Import Logs ---")
        logs = db.query(ImportLog).order_by(ImportLog.timestamp.desc()).limit(10).all()
        data = []
        for log in logs:
            data.append({
                "ID": log.id,
                "Timestamp": log.timestamp,
                "Source": log.source,
                "Added": log.records_added,
                "Updated": log.records_updated,
                "Removed": log.records_removed,
                "Status": log.status
            })
        print(pd.DataFrame(data).to_string(index=False))
        
        print("\n--- Change Logs (Sample) ---")
        changes = db.query(ChangeLog).order_by(ChangeLog.timestamp.desc()).limit(5).all()
        c_data = []
        for c in changes:
            c_data.append({
                "LogID": c.import_log_id,
                "RecordID": c.record_id,
                "Type": c.change_type,
                "Field": c.field_changed,
                "Old": (c.old_value[:20] + '...') if c.old_value and len(c.old_value) > 20 else c.old_value,
                "New": (c.new_value[:20] + '...') if c.new_value and len(c.new_value) > 20 else c.new_value
            })
        if c_data:
            print(pd.DataFrame(c_data).to_string(index=False))
        else:
            print("No changes recorded yet.")

    finally:
        db.close()

if __name__ == "__main__":
    check_logs()
