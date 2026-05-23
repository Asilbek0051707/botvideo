# Railway deployment

Railway runs one container per service. Provision them in this order, all in the
same project so they share a network and env-var references resolve.

1. **Postgres** — Add service → Database → Postgres.
2. **Redis** — Add service → Database → Redis.
3. **API** — Add service → Empty → set:
   - Source: GitHub repo
   - Root directory: `/`
   - Dockerfile: `backend/Dockerfile`
   - Start command: *(leave blank — CMD in Dockerfile is correct)*
   - Public networking: enabled
   - Variables: copy from `deploy/railway/railway.api.json`
4. **Worker** — Add service → Empty → same source, Dockerfile `worker/Dockerfile`, start command:
   `celery -A worker.celery_app.celery worker -Q default,render -l info --concurrency=2`
   Variables: copy from `deploy/railway/railway.worker.json`.
5. **Beat** — Same image, start: `celery -A worker.celery_app.celery beat -l info`.
6. **Telegram** — Dockerfile `telegram_bot/Dockerfile`, start: `python -m telegram_bot.bot`.

For GPU rendering, run the GPU worker on **RunPod** or **Vast.ai** (see those
folders); Railway does not currently offer GPU instances.

Reference env values for each Railway service are kept as JSON snippets in this
folder so you can paste them into the Variables tab.
