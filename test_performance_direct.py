import time
import pandas as pd
import io
import sys
import os

# Add current directory to path so imports work
sys.path.append(os.getcwd())

from src.db.session import SessionLocal
from src.db.models import ScreeningBatch
from src.api.routes.batch import process_batch_task
from src.api.services.engine import search_engine

def test_speed():
    # 1. Load Engine
    print("Loading engine...")
    db_engine = SessionLocal()
    search_engine.load_data(db_engine)
    db_engine.close()
    
    # 2. Generate Data
    count = 1000
    print(f"Generating test data ({count} records)...")
    # Mix of random names and known sanctions to trigger matches
    names = [f"Random Person {i}" for i in range(int(count * 0.9))]
    # Add some likely matches (assuming some exist in DB, or just generic ones)
    # Using names that likely exist in a sanctions DB
    names.extend(["Vladimir Putin", "Dmitry Medvedev", "Sergey Lavrov", "Roman Abramovich"] * int((count * 0.1) / 4))
    
    # Ensure we have exactly 'count' records
    names = names[:count]
    
    df = pd.DataFrame({"Name": names})
    
    # Convert to CSV bytes
    output = io.StringIO()
    df.to_csv(output, index=False)
    content = output.getvalue().encode("utf-8")
    
    # 3. Create Batch Record
    db_batch = SessionLocal()
    batch = ScreeningBatch(
        filename="perf_test.csv",
        total_records=len(names),
        status="PROCESSING"
    )
    db_batch.add(batch)
    db_batch.commit()
    db_batch.refresh(batch)
    batch_id = batch.id
    db_batch.close()
    
    # 4. Run Processing
    print(f"Starting processing for batch {batch_id}...")
    start_time = time.time()
    
    process_batch_task(batch_id, content, "perf_test.csv")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Processing completed in {duration:.2f} seconds")
    print(f"Rate: {len(names)/duration:.2f} records/second")

if __name__ == "__main__":
    test_speed()
