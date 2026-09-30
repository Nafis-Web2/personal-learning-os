# Run Personal Learning OS locally

## Backend
```bash
python -m venv .venv
# activate the environment
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Validate:
```bash
pytest -q
python scripts/smoke_backend.py
```

## Frontend
```bash
cd frontend
npm install --no-audit --no-fund
npm run build
npm run dev
```

Environment:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEV_USER_ID=<your local user id>
```

The current execution environment repeatedly stalls while retrieving npm dependencies, so the production Next.js build has not yet been verified here. Do not treat that as a successful frontend build.

## Current integration state
- backend unit/integration tests: validated
- fresh Alembic migration: validated
- FastAPI app boot: validated
- HTTP smoke test: validated
- frontend source/API route alignment: inspected
- npm dependency retrieval: blocked in current runtime
- Next.js production build: pending
- real AI provider: pending
- production auth/Postgres/object storage/deployment: pending
