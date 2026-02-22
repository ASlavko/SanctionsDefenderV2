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

3. **Run the API (Backend)**
   ```bash
   uvicorn src.api.main:app --reload --port 8001
   ```
   *(Note: Using port 8001 is required for the frontend to connect properly)*

4. **Run the Frontend (Next.js)**
   Open a new terminal in the `frontend` directory and run:
   ```bash
   cd frontend
   npm run dev
   ```
   The application dashboard will be accessible at: `http://localhost:3000/dashboard`

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

## Database Workflow (Neon + Alembic)

We use **Neon Database** and **Alembic** to safely manage database schemas and testing:

1. **GitHub PR Integration**: When you open a Pull Request (PR) on GitHub, a GitHub Actions workflow (`.github/workflows/neon-preview.yml`) automatically creates an isolated preview database branch in Neon.
2. **Schema Migrations**: The action automatically runs `alembic upgrade head` on the preview branch to safely apply any schema changes you made in `src/db/models.py`.
3. **Local Schema Changes**:
   - If you modify `src/db/models.py` locally, run: 
     `alembic revision --autogenerate -m "description of changes"`
   - This creates a migration script in `alembic/versions/`. Commit this script.
4. **Applying to Main**: When a PR is merged into `main`, you must ensure `alembic upgrade head` is run against the production database to apply the finalized schema changes.
