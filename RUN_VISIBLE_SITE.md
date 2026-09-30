# Run the visible Learning OS

## Terminal 1 — backend
From the project root:

```bash
python run_local.py
```

This enables the local-only learner bootstrap and starts FastAPI at `http://localhost:8000`.

## Terminal 2 — frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

The frontend will automatically create/reuse a `Local Learner` in development when `NEXT_PUBLIC_DEV_USER_ID` is not set. `/dev/bootstrap` is disabled unless `LEARNING_OS_DEV_BOOTSTRAP=1`.

## Current execution-environment limitation
The packaged source has not passed `next build` here because this environment repeatedly times out while retrieving npm dependencies. Backend tests and API smoke tests do pass. Do not treat this note as a frontend compilation certification.
