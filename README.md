# Personal Learning OS — Phase 2 Foundation

Persistent backend foundation for the Personal Learning OS.

## What is implemented
- FastAPI API and SQLAlchemy persistence
- SQLite for zero-setup local development; PostgreSQL-ready via `DATABASE_URL`
- Alembic migration foundation
- Python Foundations P0–P13 and Day Trading Foundations T0–T12 seed curricula
- Conservative prerequisite graph with 70% understanding/application gates stored per edge
- Users, replaceable auth identity mapping, enrollment, lesson progress
- Evidence-based six-dimension mastery + mastery history
- Review scheduling using the initial 1/3/7/14/30/60/120-day ladder
- Daily Gate, Gate Items, Repair Sessions
- Misconception/Mistake Bank records
- AI help-level records (0–6)
- Study sessions and compact session summaries
- Journal with Private / Learning Only / Full AI-access modes
- Learning logs separated from private journal entries
- File metadata and course links (object-storage adapter comes at deployment)
- Continuity endpoint for reconstructing a fresh tutor session
- JSON account export and user-data deletion foundation
- Automated tests for curriculum depth and an end-to-end persistence/privacy lifecycle

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```
Open `/docs` on the local API URL for interactive API documentation.

## Database
Default `.env.example` uses SQLite so the project can run without installing PostgreSQL. For deployment, set:
`DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME`

## Tests
```bash
PYTHONPATH=. pytest -q
```
Current foundation test status at handoff: **3 passed**.

## Decisions intentionally deferred until deployment
- Authentication vendor (Google/email/etc.) — database uses an adapter-friendly `auth_identities` table.
- S3-compatible object-storage vendor — database already stores ownership/metadata/storage keys.
- Hosting/database provider.
- AI model/provider integration (Phase 4).

## Phase boundary
Phase 2 establishes persistent memory and account/data architecture. Phase 3 builds the real Today / Classroom / Roadmap / Mastery / Progress / Journal UI against this backend. Phase 4 connects the conversational AI teacher.


## Phase 3 merged checkpoint
Phase 3 persistence is now merged into the Phase 2 backend. Added external learning, college courses, homework, learning resources/media usage, learner notes, dashboard API, and migration f2a166540302. Test status: 4/4 application tests pass; a clean Alembic upgrade through Phase 3 was also verified.
