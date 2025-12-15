import sys
import os
from sqlalchemy import or_

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.db.session import SessionLocal
from src.db.models import SanctionRecord
from src.core.matching import NameMatcher

def investigate_missing_normalized():
    db = SessionLocal()
    try:
        print("Investigating records with empty 'normalized_name'...")
        
        # Query for empty or null normalized_name
        # Note: In some DBs empty string is different from NULL. Checking both.
        query = db.query(SanctionRecord).filter(
            or_(
                SanctionRecord.normalized_name == None,
                SanctionRecord.normalized_name == ""
            )
        )
        
        count = query.count()
        print(f"Found {count} records with empty normalized_name.")
        
        if count > 0:
            print("\nSample of problematic records:")
            print(f"{'ID':<15} | {'List':<10} | {'Original Name':<30} | {'Aliases'}")
            print("-" * 100)
            
            samples = query.limit(20).all()
            for record in samples:
                aliases = record.alias_names if record.alias_names else "[]"
                # Truncate aliases for display
                if len(aliases) > 50:
                    aliases = aliases[:47] + "..."
                    
                print(f"{record.id:<15} | {record.list_type:<10} | {record.original_name:<30} | {aliases}")
                
                # Test normalization locally to confirm why it fails
                test_norm = NameMatcher.normalize_name(record.original_name)
                if test_norm == "":
                    print(f"   -> Normalization result: '' (Empty String)")
                else:
                    print(f"   -> Normalization result: '{test_norm}'")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    investigate_missing_normalized()
