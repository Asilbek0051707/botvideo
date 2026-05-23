# AI YouTube Factory

An automated pipeline that turns a **topic** into a finished **vertical short video**:

```
topic ──▶ script agent ──▶ scene agent ──▶ voice (TTS) ──▶ text-to-video (GPU)
        └────────────────────────────────────────────────────────┘
                                  │
                       assemble + burn captions (FFmpeg)
                                  │
                          upload to storage
                                  │
                 update DB ──▶ notify (Telegram / webhook)
```

It is built **GPU text-to-video first**, but every external dependency sits behind
an interface, so the whole pipeline **runs locally with no GPU and no paid API keys**
using FFmpeg-generated mock clips. Swap providers via `.env` to go to production.

## Stack

| Concern        | Tech |
|----------------|------|
| API            | FastAPI (async, REST + webhooks) |
| Queue          | Celery + Redis (`default`, `render`, `gpu` queues, retries) |
| Render         | FFmpeg + pluggable text-to-video (mock / Replicate / local CUDA) |
| LLM agents     | Claude (Anthropic) with OpenAI + mock fallbacks |
| Storage        | Supabase Storage (prod) / S3 / MinIO / local disk |
| DB             | Postgres (SQLAlchemy + Alembic) |
| Bot            | Telegram (end-user submit flow + admin/monitoring) |
| Monitoring     | Flower, structured logs, healthchecks |
| Deploy         | Docker Compose, Nginx+SSL, Railway/Render/VPS, RunPod/Vast.ai GPU |

## Quickstart (local, no GPU, no keys)

```bash
# 1. config
cp .env.example .env        # PowerShell: Copy-Item .env.example .env

# 2. bring up postgres, redis, minio, api, worker, beat, flower, bot
docker compose up --build -d

# 3. submit a render job
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: devkey-change-me" \
  -d '{"topic":"3 mind-blowing facts about the deep ocean","style":"documentary"}'

# 4. poll it (id from the response above)
curl http://localhost:8000/api/v1/jobs/<id> -H "X-API-Key: devkey-change-me"
```

With the default mock providers this produces a **real `.mp4`** (synthetic visuals +
silent/again-mock voice track + burned captions) and stores it in MinIO. The
`video_url` in the job response is directly playable.

- API docs: http://localhost:8000/docs
- Task monitor (Flower): http://localhost:5555 (admin/admin)
- Object store console (MinIO): http://localhost:9001 (minioadmin/minioadmin)

## Going to production

Set real providers in `.env`:

```ini
LLM_PROVIDER=anthropic       ANTHROPIC_API_KEY=sk-ant-...
TTS_PROVIDER=elevenlabs      ELEVENLABS_API_KEY=...
T2V_PROVIDER=replicate       REPLICATE_API_TOKEN=...     # or =gpu on a CUDA box
STORAGE_BACKEND=supabase     SUPABASE_URL=... SUPABASE_SERVICE_KEY=...
TELEGRAM_BOT_TOKEN=...        TELEGRAM_ADMIN_IDS=11111111
```

For real GPU rendering on RunPod / Vast.ai:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

See **[docs/INSTALL.md](docs/INSTALL.md)**, **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**,
**[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**, and **[docs/ROADMAP.md](docs/ROADMAP.md)**.

## Layout

```
factory/            # shared importable package (the core)
  core/             # settings, logging, security
  db/               # SQLAlchemy models + session
  schemas/          # pydantic request/response models
  agents/           # script / scene / voice / visual / seo agents + orchestrator
  prompts/          # versioned Claude prompt templates
  render/           # FFmpeg pipeline, captions, assembler, T2V providers
  storage/          # storage interface + local/minio/s3/supabase adapters
  services/         # job service, queue, notifications
backend/            # FastAPI app (API routes, webhooks)
worker/             # Celery app + tasks (CPU + GPU Dockerfiles)
telegram_bot/       # Telegram bot (user + admin handlers)
database/           # schema.sql, seed.sql, alembic migrations
deploy/             # nginx, certbot, systemd, railway/render/runpod/vast
docs/               # architecture, install, deployment, roadmap
frontend/           # (optional) Next.js dashboard scaffold
```

> Naming note: the spec's `agents/`, `prompts/`, `render engine/` live inside the
> single `factory/` package so the API, worker, and bot share one source of truth
> instead of duplicating code or hacking `sys.path`.
