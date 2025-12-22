import sys, os
# Ensure workspace root is on sys.path
ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(ROOT, os.pardir))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from src.db.session import SessionLocal
from src.db.models import ScreeningBatch
from src.api.routes.batch import process_batch_task, read_csv_robust

def run_batch(file_path: str):
    # Initialize search engine with data
    from src.api.services.engine import search_engine
    with SessionLocal() as db:
        search_engine.load_data(db)
    print("Search engine initialized with sanctions data")
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return 1

    filename = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        content = f.read()

    # Pre-count records to set total_records
    try:
        import io
        import pandas as pd
        if filename.endswith('.csv'):
            df = read_csv_robust(content)
        else:
            df = pd.read_excel(io.BytesIO(content))
        total = len(df)
    except Exception as e:
        print(f"Failed to read file for counting: {e}")
        total = 0

    with SessionLocal() as db:
        batch = ScreeningBatch(
            filename=filename,
            total_records=total,
            status="PROCESSING"
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)
        batch_id = batch.id

    # Run processing task (creates its own DB session)
    process_batch_task(batch_id, content, filename)

    # Summarize results
    with SessionLocal() as db:
        b = db.query(ScreeningBatch).filter(ScreeningBatch.id == batch_id).first()
        if not b:
            print(f"Batch {batch_id} not found after processing")
            return 1
        print(f"Batch {batch_id} completed. Total={b.total_records}, Flagged={b.flagged_count}, Status={b.status}")
    return 0

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else r"C:\\Users\\Slavko\\SanctionDefenderV2\\test_upload_files\\celoten seznam.csv"
    exit(run_batch(file_path))
