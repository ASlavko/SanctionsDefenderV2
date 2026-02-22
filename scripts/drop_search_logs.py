
from src.db.session import engine
from sqlalchemy import text

def drop_table():
    print("Connecting to database...")
    with engine.connect() as conn:
        print("Dropping search_logs table...")
        conn.execute(text("DROP TABLE search_logs"))
        conn.commit()
    print("Table dropped successfully.")

if __name__ == "__main__":
    try:
        drop_table()
    except Exception as e:
        print(f"Error: {e}")
