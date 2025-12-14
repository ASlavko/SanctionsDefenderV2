from sqlalchemy import func
from src.db.session import SessionLocal
from src.db.models import SanctionRecord
import pandas as pd

def analyze_breakdown():
    db = SessionLocal()
    try:
        print("--- Breakdown by Source (List Type) ---")
        source_counts = db.query(
            SanctionRecord.list_type, 
            func.count(SanctionRecord.id)
        ).group_by(SanctionRecord.list_type).all()
        
        df_source = pd.DataFrame(source_counts, columns=["Source", "Count"])
        print(df_source.to_string(index=False))
        print("\n")

        print("--- Breakdown by Entity Type ---")
        type_counts = db.query(
            SanctionRecord.entity_type, 
            func.count(SanctionRecord.id)
        ).group_by(SanctionRecord.entity_type).all()
        
        # Handle None values for display
        cleaned_type_counts = []
        for etype, count in type_counts:
            cleaned_type_counts.append((etype if etype else "Unknown/None", count))
            
        df_type = pd.DataFrame(cleaned_type_counts, columns=["Entity Type", "Count"])
        print(df_type.to_string(index=False))
        print("\n")

        print("--- Detailed Breakdown (Source x Entity Type) ---")
        detailed_counts = db.query(
            SanctionRecord.list_type,
            SanctionRecord.entity_type,
            func.count(SanctionRecord.id)
        ).group_by(SanctionRecord.list_type, SanctionRecord.entity_type).all()
        
        cleaned_detailed = []
        for source, etype, count in detailed_counts:
            cleaned_detailed.append((source, etype if etype else "Unknown/None", count))

        df_detailed = pd.DataFrame(cleaned_detailed, columns=["Source", "Entity Type", "Count"])
        # Pivot for better readability
        pivot_df = df_detailed.pivot(index="Source", columns="Entity Type", values="Count").fillna(0).astype(int)
        print(pivot_df.to_string())

    except Exception as e:
        print(f"Error analyzing data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    analyze_breakdown()
