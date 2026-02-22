from src.db.session import engine, Base
from src.db.models import ScreeningResult, ScreeningMatch
from sqlalchemy import text

def recreate_tables():
    print("Dropping screening tables...")
    # Use CASCADE to handle dependent types/constraints
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS screening_matches CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS screening_results CASCADE"))
        conn.commit()
    
    print("Creating new tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")

if __name__ == "__main__":
    recreate_tables()