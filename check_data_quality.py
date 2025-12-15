import sys
import os
from sqlalchemy import text, func, or_

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.db.session import SessionLocal
from src.db.models import SanctionRecord

def check_empty_fields():
    db = SessionLocal()
    try:
        print("Analyzing 'sanctions' table for empty/NULL values...")
        
        total_count = db.query(SanctionRecord).count()
        print(f"Total Records: {total_count}")
        print("-" * 60)
        print(f"{'Field Name':<20} | {'Empty/Null Count':<18} | {'% Empty':<10}")
        print("-" * 60)

        # List of fields to check
        fields = [
            "id", "list_type", "original_name", "normalized_name", 
            "alias_names", "program", "nationality", "birth_date", 
            "entity_type", "gender", "url", "un_id", "remark", "function",
            "is_active", "last_updated", "first_seen", "last_seen"
        ]

        for field_name in fields:
            column = getattr(SanctionRecord, field_name)
            
            # Count where column is NULL or empty string
            # Note: For non-string columns (DateTime, Boolean), we only check NULL
            if str(column.type) in ['STRING', 'TEXT', 'VARCHAR']:
                empty_count = db.query(SanctionRecord).filter(
                    or_(column == None, column == "")
                ).count()
            else:
                empty_count = db.query(SanctionRecord).filter(column == None).count()

            percentage = (empty_count / total_count) * 100 if total_count > 0 else 0
            print(f"{field_name:<20} | {empty_count:<18} | {percentage:.1f}%")

        print("-" * 60)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_empty_fields()
