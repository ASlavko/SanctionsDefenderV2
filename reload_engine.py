from src.db.session import SessionLocal
from src.api.services.engine import search_engine

db = SessionLocal()
try:
    print("Reloading search engine with updated data...")
    search_engine.load_data(db)
    print("Search engine reloaded successfully!")
    
    # Get status
    status = search_engine.get_status()
    print(f"\nSearch Engine Status:")
    print(f"Sanctions loaded: {status['sanctions_loaded']}")
    print(f"Unique records: {status['unique_records']}")
    print(f"Decisions loaded: {status['decisions_loaded']}")
finally:
    db.close()
