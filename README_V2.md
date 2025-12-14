# SanctionDefender V2

## Setup

1. **Environment Variables**
   Create a `.env` file in the root directory:
   ```
   DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
   ```
   (For local testing without Postgres, it defaults to `sqlite:///./test.db`)

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API**
   ```bash
   uvicorn src.api.main:app --reload
   ```

## Features

- **Hybrid Architecture**: Postgres for storage, In-Memory for search.
- **Batch Screening**: Upload Excel/CSV files via `/api/v1/batch/upload`.
- **Decision Memory**: Remembers false positives (logic implemented in `SearchEngine`).
- **ETL Pipeline**: `src/etl/loader.py` handles daily updates (New/Updated/Inactive).

## Project Structure

- `src/api`: FastAPI application and routes.
- `src/core`: Core logic (matching, normalization).
- `src/db`: Database models and session.
- `src/etl`: Parsers and Loader for daily updates.
