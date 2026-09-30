# Deployment readiness

This checkpoint removes local-only assumptions from the backend.

- CORS origins are configured by `ALLOWED_ORIGINS`.
- `/dev/bootstrap` is unavailable whenever `APP_ENV=production`.
- `start_production.sh` applies Alembic migrations before Uvicorn starts.
- `/health` is available for hosting health checks.
- `render.yaml` describes a preview backend web service.
- secrets remain environment variables and are never bundled.
- `DATABASE_URL` remains portable between SQLite development and PostgreSQL deployment.
- frontend has a Vercel-compatible configuration, but its production build still requires a normal npm-capable environment.

Important: Render's free PostgreSQL tier expires after 30 days. Do not use it as the permanent Learning OS database. A durable managed PostgreSQL provider should be selected before real personal learning history is entrusted to the deployed app.
