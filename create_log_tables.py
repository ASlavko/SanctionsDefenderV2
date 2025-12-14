from src.db.session import engine, Base
from src.db.models import ImportLog, ChangeLog

def create_tables():
    print("Creating tables for ImportLog and ChangeLog...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    create_tables()
