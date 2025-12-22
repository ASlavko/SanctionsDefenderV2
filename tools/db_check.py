import os, sys
from pathlib import Path
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import text

# Ensure workspace root is on sys.path
ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(ROOT, os.pardir))
if ROOT not in sys.path:
    sys.path.append(ROOT)

# Load .env explicitly before importing session
ENV_PATH = Path(ROOT) / ".env"
print("ENV PATH:", ENV_PATH)
try:
    with open(ENV_PATH, 'r', encoding='utf-8') as f:
        print(".env contents:")
        print(f.read())
except Exception as e:
    print("Failed to read .env:", repr(e))
load_dotenv(dotenv_path=str(ENV_PATH), override=True)
print("ENV DATABASE_URL:", os.getenv("DATABASE_URL"))

from src.db.session import engine, SessionLocal

print("Engine URL:", str(engine.url))
print("Dialect:", engine.dialect.name)

with SessionLocal() as db:
    try:
        if engine.dialect.name == 'postgresql':
            # Show server & db info
            info = db.execute(text("select current_database(), version()"))
            print("DB Info:", list(info))
        cnt_batches = db.execute(text("select count(*) from screening_batches"))
        max_id = db.execute(text("select max(id) from screening_batches"))
        print("screening_batches count:", list(cnt_batches)[0][0])
        print("screening_batches max id:", list(max_id)[0][0])
    except Exception as e:
        print("DB check error:", repr(e))
