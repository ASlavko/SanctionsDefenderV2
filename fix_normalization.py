import sys
import os
from sqlalchemy import or_

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.db.session import SessionLocal
from src.db.models import SanctionRecord
from src.core.matching import NameMatcher

def fix_normalization():
    db = SessionLocal()
    try:
        print("Starting normalization fix...")
        
        # 1. Get all records (we should re-normalize everything to be safe, 
        # or at least the ones that are empty)
        # Let's start with the empty ones to fix the immediate issue.
        records = db.query(SanctionRecord).filter(
            or_(
                SanctionRecord.normalized_name == None,
                SanctionRecord.normalized_name == ""
            )
        ).all()
        
        print(f"Found {len(records)} records with empty normalized_name.")
        
        count = 0
        for record in records:
            new_norm = NameMatcher.normalize_name(record.original_name)
            
            if new_norm != record.normalized_name:
                record.normalized_name = new_norm
                count += 1
                
                if count % 100 == 0:
                    print(f"Fixed {count} records...")
                    db.commit()
        
        db.commit()
        print(f"Successfully fixed {count} records.")
        
        # Optional: Verify one
        if count > 0:
            print(f"Verification: {records[0].original_name} -> {records[0].normalized_name}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_normalization()
