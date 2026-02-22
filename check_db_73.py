from src.db.session import SessionLocal
from src.db.models import ScreeningResult, ScreeningBatch

db = SessionLocal()
batch_id = 74
batch = db.query(ScreeningBatch).filter(ScreeningBatch.id == batch_id).first()
print(f"Batch {batch_id}: {batch.filename}, status={batch.status}")

results = db.query(ScreeningResult).filter(ScreeningResult.batch_id == batch_id).all()
print(f"Total results: {len(results)}")
for r in results:
    print(f"Result ID: {r.id}, Input: {r.input_name}")
db.close()
